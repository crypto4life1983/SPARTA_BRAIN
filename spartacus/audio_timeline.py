from __future__ import annotations

import math


def validate_voice_master_timeline(
    scenes: list[dict],
    fps: int = 30,
    scene_buffer_sec: float = 0.30,
    final_hold_sec: float = 0.40,
) -> None:
    """Fail fast if generated scene timing can cut or fade voice audio."""
    if not scenes:
        return
    for idx, scene in enumerate(scenes):
        scene_no = idx + 1
        start_f = int(scene.get("startFrame", 0) or 0)
        dur_f = int(scene.get("durationInFrames", 0) or 0)
        audio_dur_f = math.ceil(float(scene.get("audioDuration", 0.0) or 0.0) * fps)
        delay_f = round(float(scene.get("audioDelay", 0.0) or 0.0) * fps)
        voice_end_f = start_f + delay_f + audio_dur_f
        scene_end_f = start_f + dur_f
        required_end_f = voice_end_f + round(scene_buffer_sec * fps)
        if scene_end_f < required_end_f:
            raise RuntimeError(
                f"Voice-master timeline failed: scene {scene_no} ends before voice + "
                f"{scene_buffer_sec:.1f}s buffer"
            )

        if idx + 1 < len(scenes):
            next_start_f = int(scenes[idx + 1].get("startFrame", 0) or 0)
            if next_start_f < voice_end_f:
                raise RuntimeError(
                    f"Voice-master timeline failed: scene {scene_no} transition starts before voice ends"
                )

        if idx == len(scenes) - 1:
            final_hold_f = scene_end_f - voice_end_f
            if final_hold_f < round(final_hold_sec * fps):
                raise RuntimeError(
                    f"Voice-master timeline failed: final scene hold is less than {final_hold_sec:.1f}s"
                )

        sub_start = int(scene.get("subtitleStart", 0) or 0)
        sub_end = int(scene.get("subtitleEnd", 0) or 0)
        if sub_start < 0 or sub_end > dur_f:
            raise RuntimeError(
                f"Voice-master timeline failed: scene {scene_no} subtitles extend outside scene duration"
            )
        for chunk in scene.get("subtitleChunks") or []:
            chunk_start = int(chunk.get("start", 0) or 0)
            chunk_end = int(chunk.get("end", 0) or 0)
            if chunk_start < 0 or chunk_end > dur_f:
                raise RuntimeError(
                    f"Voice-master timeline failed: scene {scene_no} subtitle chunk extends outside scene duration"
                )

        fade_start = scene.get("audioFadeStart", scene.get("audioFadeOutStart"))
        if fade_start is not None:
            fade_start_f = round(float(fade_start) * fps)
            if start_f + fade_start_f < voice_end_f:
                raise RuntimeError(
                    f"Voice-master timeline failed: scene {scene_no} audio fade starts before voice ends"
                )
