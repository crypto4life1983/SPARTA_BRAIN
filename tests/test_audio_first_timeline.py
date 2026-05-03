import pytest

from spartacus.audio_timeline import validate_voice_master_timeline


FPS = 30


def scene(start, duration, voice, *, subtitle_end=None, chunks=None, fade_start=None):
    duration_f = round(duration * FPS)
    data = {
        "startFrame": round(start * FPS),
        "durationInFrames": duration_f,
        "audioDuration": voice,
        "audioDelay": 0.0,
        "subtitleStart": 0,
        "subtitleEnd": duration_f if subtitle_end is None else round(subtitle_end * FPS),
        "subtitleChunks": chunks if chunks is not None else [
            {"text": "caption", "start": 0, "end": duration_f}
        ],
    }
    if fade_start is not None:
        data["audioFadeStart"] = fade_start
    return data


def test_voice_master_timeline_accepts_valid_scene_sequence():
    scenes = [
        scene(0.0, 1.4, 1.0),
        scene(1.4, 1.4, 1.0),
        scene(2.8, 1.5, 1.0),
    ]

    validate_voice_master_timeline(scenes, fps=FPS)


def test_voice_master_timeline_rejects_scene_shorter_than_voice_plus_buffer():
    scenes = [
        scene(0.0, 1.26, 1.0),
        scene(1.26, 1.5, 1.0),
    ]

    with pytest.raises(RuntimeError, match="voice \\+ 0.3s buffer"):
        validate_voice_master_timeline(scenes, fps=FPS)


def test_voice_master_timeline_rejects_transition_before_voice_ends():
    scenes = [
        scene(0.0, 2.0, 1.5),
        scene(1.4, 1.5, 1.0),
    ]

    with pytest.raises(RuntimeError, match="transition starts before voice ends"):
        validate_voice_master_timeline(scenes, fps=FPS)


def test_voice_master_timeline_rejects_final_hold_under_400ms():
    scenes = [
        scene(0.0, 1.4, 1.0),
        scene(1.4, 1.35, 1.0),
    ]

    with pytest.raises(RuntimeError, match="final scene hold"):
        validate_voice_master_timeline(scenes, fps=FPS)


def test_voice_master_timeline_rejects_subtitles_outside_scene_duration():
    scenes = [
        scene(0.0, 1.4, 1.0),
        scene(1.4, 1.5, 1.0, subtitle_end=1.6),
    ]

    with pytest.raises(RuntimeError, match="subtitles extend outside scene duration"):
        validate_voice_master_timeline(scenes, fps=FPS)


def test_voice_master_timeline_rejects_subtitle_chunks_outside_scene_duration():
    scenes = [
        scene(0.0, 1.4, 1.0),
        scene(1.4, 1.5, 1.0, chunks=[
            {"text": "caption", "start": 0, "end": round(1.6 * FPS)}
        ]),
    ]

    with pytest.raises(RuntimeError, match="subtitle chunk extends outside scene duration"):
        validate_voice_master_timeline(scenes, fps=FPS)


def test_voice_master_timeline_rejects_audio_fade_before_voice_ends():
    scenes = [
        scene(0.0, 1.4, 1.0),
        scene(1.4, 1.5, 1.0, fade_start=0.8),
    ]

    with pytest.raises(RuntimeError, match="audio fade starts before voice ends"):
        validate_voice_master_timeline(scenes, fps=FPS)
