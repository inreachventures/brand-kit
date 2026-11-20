import zipfile

import pytest

from brandkit import BrandKitError, pack


def _tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_pack_roundtrip(brand_dir, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("elsewhere")
    (brand_dir / "assets" / "x.bin").write_bytes(bytes(range(256)))
    (brand_dir / ".DS_Store").write_bytes(b"junk")
    (brand_dir / "assets" / "__pycache__").mkdir()
    (brand_dir / "assets" / "__pycache__" / "a.pyc").write_bytes(b"junk")
    z = pack.pack(brand_dir, tmp_path / "out" / "brand.zip")
    assert z.is_file()
    with zipfile.ZipFile(z) as zf:
        assert all(n.startswith("brand/") for n in zf.namelist())
    dest = tmp_path / "dest"
    out = pack.unpack(z, dest)
    assert out == dest / "brand"
    expected = {k: v for k, v in _tree(brand_dir).items() if ".DS_Store" not in k and "__pycache__" not in k}
    assert _tree(out) == expected


def test_unpack_rejects_traversal(tmp_path):
    z = tmp_path / "evil.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("../evil.txt", "x")
    with pytest.raises(BrandKitError):
        pack.unpack(z, tmp_path / "dest")
    assert not (tmp_path / "evil.txt").exists()


def test_unpack_rejects_absolute(tmp_path):
    z = tmp_path / "evil.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("/abs.txt", "x")
    with pytest.raises(BrandKitError):
        pack.unpack(z, tmp_path / "dest")


def test_unpack_requires_brand_dir(tmp_path):
    z = tmp_path / "nobrand.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("other/a.txt", "x")
    with pytest.raises(BrandKitError):
        pack.unpack(z, tmp_path / "dest")


def test_unpack_bad_zip(tmp_path):
    z = tmp_path / "bad.zip"
    z.write_text("not a zip")
    with pytest.raises(BrandKitError):
        pack.unpack(z, tmp_path / "dest")


def test_unpack_refuses_non_empty_brand(brand_dir, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("elsewhere")
    z = pack.pack(brand_dir, tmp_path / "brand.zip")
    dest = tmp_path / "dest"
    (dest / "brand" / "strategy").mkdir(parents=True)
    (dest / "brand" / "strategy" / "audience-old.md").write_text("old")
    with pytest.raises(BrandKitError, match="empty folder"):
        pack.unpack(z, dest)
    assert not (dest / "brand" / "style-guide").exists()


def test_unpack_into_empty_brand_folder_is_fine(brand_dir, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("elsewhere")
    z = pack.pack(brand_dir, tmp_path / "brand.zip")
    dest = tmp_path / "dest"
    (dest / "brand").mkdir(parents=True)
    assert (pack.unpack(z, dest) / "style-guide" / "tokens.json").is_file()


def test_pack_handles_pre_1980_mtime(brand_dir, tmp_path):
    import os
    f = brand_dir / "assets" / "old.txt"
    f.write_text("x")
    os.utime(f, (0, 0))
    z = pack.pack(brand_dir, tmp_path / "out.zip")
    with zipfile.ZipFile(z) as zf:
        assert "brand/assets/old.txt" in zf.namelist()
