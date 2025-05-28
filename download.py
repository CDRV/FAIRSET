import argparse
import importlib
import io
import json
import os
import re
import shutil
from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain
from pathlib import Path
from typing import List
from urllib.parse import urlparse
from zipfile import ZipFile

import requests
import unzip_http

WIDER_FACE_ANNOTATIONS = "http://shuoyang1213.me/WIDERFACE/support/bbx_annotation/wider_face_split.zip"
WIDER_FACE_TRAIN = "https://huggingface.co/datasets/CUHK-CSE/wider_face/resolve/main/data/WIDER_train.zip"
WIDER_FACE_VAL = "https://huggingface.co/datasets/CUHK-CSE/wider_face/resolve/main/data/WIDER_val.zip"

AMAZON_LABELS = "https://github.com/amazon-science/widerface-demographics/archive/refs/heads/main.zip"


def parse_args():
    parser = argparse.ArgumentParser(description="Download and prepare FairSet dataset")
    parser.add_argument("-a", "--alexa", action="store_true", help="Download the Amazon Alexa annotations")
    parser.add_argument(
        "-r",
        "--regenerate",
        action="store_true",
        help="Regenerate the merged Amazon Alexa / Widerface annotations, if downloaded. Can be used with -a/--alexa",
    )
    parser.add_argument(
        "-d",
        "--dad3d",
        action="store",
        help="Specify the location or the download link of the DAD3D-Heads dataset",
        required=True,
    )
    parser.add_argument(
        "-w",
        "--widerface",
        action="store",
        nargs="+",
        help="Specify the location of the widerface zip(s).\
                                Optional. If no zip is specified, this script will try to\
                                fetch and extract the specific images",
        type=str,
        default=(WIDER_FACE_TRAIN, WIDER_FACE_VAL),
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force download the dataset even if it seems present"
    )
    parser.add_argument(
        "-o", "--output", action="store", default="assets", type=str, help="Directory to download the dataset to"
    )

    return parser.parse_args()


def wget_zip(url: str, path2extract: Path):
    r = requests.get(url)
    z = ZipFile(io.BytesIO(r.content))

    Path(path2extract).mkdir(parents=True, exist_ok=True)
    z.extractall(path2extract)


def is_path_remote(path):
    is_remote = urlparse(path).scheme in ("http", "https", "ftp")

    if not is_remote and not Path(path).exists():
        raise ValueError(f"Invalid url or dataset path: {path}.\nIf a download link was provided, it might be expired.")

    return is_remote


def list_fairset(path: Path):
    with path.open("r") as f:
        return list(json.load(f).keys())


class FairsetSourceType(Enum):
    WIDERFACE = auto()
    DAD3DHEADS = auto()


@dataclass
class FairsetDwnld:
    type: FairsetSourceType
    urls: List[str]
    remote: bool = True


def parse_dad3d_files(all_files: List[str], reject: bool = False) -> List[str]:
    """
    Parse the FAIRSET filenames to segragate widerface and DAD3D-Heads images.
    :param all_files: list of all files in FAIRSET
    :param reject: if False, return the DAD3D-Heads files, if True, return the WIDERFACE files
    """
    # DAD3D-Heads dataset images are named with guid
    guid_regex = re.compile(
        "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", re.I
    )  # https://stackoverflow.com/a/42048037
    return [f for f in all_files if bool(guid_regex.match(f)) != reject]


def list_fairset_imgs(source: FairsetSourceType):
    files = list_fairset(Path("./fairset.json"))
    return parse_dad3d_files(files, reject=(source == FairsetSourceType.WIDERFACE))


def get_missing_fairset_imgs(assets_dir: Path, source: FairsetSourceType) -> List[str]:
    files = list_fairset_imgs(source)
    if assets_dir.exists():
        return list(set(files) - set(os.listdir(assets_dir)))


def dwnld_fairset(data_dir: Path, download_type: FairsetDwnld, files: List[str] = None):
    if files is None:
        files = list_fairset_imgs(download_type.type)

    dwnld_files_count = 0
    for url in download_type.urls:
        rzf = unzip_http.RemoteZipFile(url) if download_type.remote else ZipFile(url, "r")

        # match image file names to full paths
        try:
            paths = rzf.namelist()
        except KeyError as e:
            print(
                f"\033[91mRemote ZIP header did not return the Content-Length header... You will need to download the zip manually: {url}\033[0m"
            )
            continue  # Trying the next widerface url
        except Exception as e:
            print(
                f"\033[91mError while reading ZIP file header: {e}\nYou might have to download the zip manually {url}\033[0m"
            )
            continue  # Trying the next widerface url

        paths = {p.split("/")[-1]: p for p in paths if p.endswith(".jpg") or p.endswith(".png")}
        files_full_paths = [paths[f] for f in files if f in paths]

        if files_full_paths:
            # download selected images
            data_dir.mkdir(parents=True, exist_ok=True)

            try:
                rzf.extractall(path=data_dir, members=files_full_paths)
            except Exception as e:
                print(f"\033[91mError while extracting files: {e}\033[0m")
                continue  # Trying the next widerface url
            finally:
                if isinstance(rzf, ZipFile):
                    rzf.close()

        dwnld_files_count += len(files_full_paths)

    if dwnld_files_count != len(files):
        print(f"\033[91mDownloaded {dwnld_files_count} images, expected {len(files)}\033[0m")


def dwnld_widerface(data_dir: Path, remote_data: List, force: bool = False):
    """
    Download WIDERFACE dataset from the official website or extract images from local zip files
    FAIRSET images only
    :param ... TODO
    :param force: force download even if the dataset seems already present
    """
    widerface_imgs = get_missing_fairset_imgs(data_dir, FairsetSourceType.WIDERFACE)
    if force or not data_dir.exists() or len(widerface_imgs) > 0:
        is_remote = all(
            [is_path_remote(url) for url in remote_data]
        )  # TODO: fails if the user provides a mix of URL and local zips

        dwnld_fairset(
            data_dir, FairsetDwnld(FairsetSourceType.WIDERFACE, remote_data, remote=is_remote), files=widerface_imgs
        )


def dwnld_alexa_annots(amazon_dir: Path, force: bool = False):
    """
    Download Amazon Alexa demographics annotations for Widerface
    :param amazon_dir: path to download the annotations to
    :param force: force download even if the annotations seem already present
    """
    if force or not amazon_dir.exists() or len(os.listdir(amazon_dir)) == 0:
        wget_zip(AMAZON_LABELS, amazon_dir)
        return True
    return False


def patch_alexa_merging_script(module: Path):
    """
    Patch the Amazon Alexa script to merge Amazon annotations with Widerface ones
    :param module: path to the merging script
    """
    cwd = Path(os.getcwd())
    os.chdir(cwd / module.parent)

    with open(module.stem + ".py", "r+") as f:
        script = f.read().split("\n")

        script.insert(15, "\tskip_image = False")
        script.insert(19, "\t\t\tskip_image = False")
        script.insert(21, "\t\tif skip_image:\n\t\t\tcontinue")
        script.insert(24, "\t\t\tif num_users == 0:\n\t\t\t\tskip_image = True")

        f.seek(0)
        f.write("\n".join(script))  # should overwrite since new content is longer than previous script

    os.chdir(cwd)


def merge_alexa_annots(assets_dir: Path, amazon_dir: Path, wf_labels_dir: Path, patch=True):

    module = Path(f"{amazon_dir}/widerface-demographics-main/scripts/update_demographics_for_annotations")
    if patch:
        patch_alexa_merging_script(module)

    importlib.invalidate_caches()
    amazon = importlib.import_module(re.sub("(\\\\|\/)", ".", str(module)), package=__name__)

    (annotations_dir := assets_dir / "alexa").mkdir(parents=True, exist_ok=True)
    amz_args = [
        amazon_dir / "widerface-demographics-main/annotations/demographics_train.csv",
        wf_labels_dir / "wider_face_train_bbx_gt.txt",
        annotations_dir / "train.csv",
    ]

    # Merge training and validation annotations
    for _ in range(2):
        amazon.add_demographic_annotations(*amz_args)
        amz_args = [Path(str(arg).replace("train", "val")) for arg in amz_args]

    # Combine the train and valid files
    with open(annotations_dir / "val.csv", "r") as fval:
        with open(annotations_dir / "train.csv", "a") as ftrain:
            lines = [f.replace("images/", "") for f in fval.readlines()[1:]]
            ftrain.write("".join(lines))

    shutil.move(annotations_dir / "train.csv", annotations_dir / "annotations.csv")
    (annotations_dir / "val.csv").unlink()


def dwnld_dad3d(data_dir: Path, dad3d_dir: str, force: bool = False):
    dad3dheads_imgs = get_missing_fairset_imgs(data_dir, FairsetSourceType.DAD3DHEADS)
    data_dir /= "dad3dheads"

    if force or not data_dir.parent.exists() or len(dad3dheads_imgs) > 0:
        is_remote = is_path_remote(dad3d_dir)

        # Download the DAD3D-Heads dataset from the given URL or local zip file
        dwnld_fairset(
            data_dir, FairsetDwnld(FairsetSourceType.DAD3DHEADS, (dad3d_dir,), remote=is_remote), files=dad3dheads_imgs
        )


def cleanup(data_dir: Path, wf_labels_dir: Path, amazon_dir: Path):
    directories = [child for child in data_dir.iterdir() if child.is_dir()]

    # Move all images to the data directory
    images = chain(data_dir.rglob("**/*.jpg"), data_dir.rglob("**/*.png"))
    for f in images:
        shutil.move(str(f), data_dir / f.name)

    for d in directories:
        shutil.rmtree(d)

    # Delete the intermediate directories for Widerface and Amazon raw annotations
    shutil.rmtree(wf_labels_dir, ignore_errors=True)
    shutil.rmtree(amazon_dir, ignore_errors=True)


if __name__ == "__main__":
    args = parse_args()

    FAIRSET_SIZE = len(list_fairset(Path("./fairset.json")))

    assets_dir = Path(args.output)
    data_dir = assets_dir / "FAIRSET"

    alexa_dir = assets_dir / "alexa"
    wf_labels_dir = alexa_dir / "wider_face_split"

    #  Download the FAIRSET subsets from Widerface and DAD3D-Heads
    print("\n--> Downloading WIDERFACE subset...")
    dwnld_widerface(data_dir, args.widerface, args.force)

    print("--> Downloading/extracting DAD3D-Heads subset...")
    dwnld_dad3d(data_dir, args.dad3d, args.force)

    # Download the Amazon Alexa Widerface annotations
    if args.alexa:
        print("--> Downloading Alexa annotations...")

        # Download the Amazon Alexa demographics annotations
        fresh_dwnld = dwnld_alexa_annots(alexa_dir, args.force or args.regenerate)

        if fresh_dwnld:  # Download the widerface annotations
            wget_zip(WIDER_FACE_ANNOTATIONS, wf_labels_dir.parent)

        if fresh_dwnld:  # Merge the Amazon Alexa annotations with the WIDERFACE ones
            print("--> Generating the full Alexa annotations...")
            merge_alexa_annots(assets_dir, alexa_dir, wf_labels_dir, patch=fresh_dwnld)

    print("--> Cleaning up...")
    cleanup(data_dir, wf_labels_dir, alexa_dir / "widerface-demographics-main")

    if (len_dwnld := len(list(data_dir.iterdir()))) == FAIRSET_SIZE:
        print(f"\033[92mALL GOOD\033[0m")
    else:
        print(f"\033[91mMISSING images... Downloaded {len_dwnld}/{FAIRSET_SIZE}\033[0m")
