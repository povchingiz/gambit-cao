"""Unit tests for GAMBIT Avatar Studio & Renderer CLI."""

import json
from pathlib import Path

from run.gambit_render import AvatarStudioRenderer


def test_avatar_studio_voicebox_render(tmp_path: Path):
    renderer = AvatarStudioRenderer(output_dir=tmp_path)
    out_wav = tmp_path / "test_voice.wav"

    res = renderer.render_voicebox(text="Testing voice synthesis", output_path=out_wav)

    assert res["status"] == "success"
    assert out_wav.exists()
    assert out_wav.stat().st_size > 100
    assert res["viseme_frames"] > 0


def test_avatar_studio_hunyuan_render(tmp_path: Path):
    renderer = AvatarStudioRenderer(output_dir=tmp_path)
    out_mp4 = tmp_path / "test_hunyuan.mp4"

    res = renderer.render_hunyuan_avatar(
        text="Clinical consultation on CBCT dental implant",
        output_path=out_mp4,
        emotion="confident",
        fps=25,
    )

    assert res["status"] == "success"
    assert res["engine"] == "hunyuan_avatar_mmdit"
    assert out_mp4.exists()
    assert out_mp4.stat().st_size > 0
    assert res["job_spec"]["emotion_prior"] == "confident"

    meta_file = Path(res["metadata_file"])
    assert meta_file.exists()
    meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
    assert meta_data["model"] == "Tencent-Hunyuan/HunyuanVideo-Avatar"
