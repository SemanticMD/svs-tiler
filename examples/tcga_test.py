__author__ = 'sb'
from utilities_lib import get_imgfiles, transfer_to_s3
import os.path
import csv
from io import BytesIO
from models.pathology import handle_pathology
import requests
from shutil import move

svs_files_dir = '/media/sb/Toshiba External/tcga-pathology'
svs_files_dir2 = '/media/sb/Toshiba\ External/tcga-pathology'
labels_file = 'histogram_noDuke_rscale_kmeans_k150_labels.csv'
session_id = '7e99003828b64dd4883868684bcde7f3'
zoom_level = 12


def create_session():
    rv = requests.post(
        url="https://api.semantic.md/tag/" + 'tcga',
        data={
            "image_url": 'img.medicalxpress.com/newman/gfx/news/hires/2015/melanoma.jpg'
        }
    )

    session_id = rv.json()["dataset_id"]

    return session_id


def tag_image(session_id, tag_name, img_url):
    rv = requests.put(
        url="https://api.semantic.md/dataset/" + session_id + '/' + tag_name,
        data={
            "image_url": img_url
        }
    )

    return rv.status_code


def img_files_to_s3_urls(img_files):
    s3_urls = []

    for img_file in img_files:
        fp = open(img_file, mode='rb')
        _, file_extension = os.path.splitext(img_file)
        s3_urls.append(transfer_to_s3(BytesIO(fp.read()), file_extension))

    return s3_urls


def _svs_fname2tcga_id(svs_fname):
    tcga_id = svs_fname.split("-")[0:3]
    tcga_id.append("01")
    tcga_id = "-".join(tcga_id)

    return tcga_id


def get_tcga_labels():
    tcga2idh1 = {}

    with open(os.path.join(svs_files_dir, labels_file), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            tcga2idh1[row[0]] = row[-1]

    return tcga2idh1


def create_dz_files(img_files_list):
    tcga2idh1 = get_tcga_labels()

    if img_files_list is None:
        img_files_list = get_imgfiles(svs_files_dir)

    for svs_file in img_files_list:
        svs_filename = os.path.basename(svs_file).split(".")[0]
        tcga_id = _svs_fname2tcga_id(svs_filename)

        if tcga_id in tcga2idh1:
            outdir = os.path.join(svs_files_dir, svs_filename)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            else:
                print(outdir)
                continue
            my_file = (os.path.join(svs_files_dir2, os.path.basename(svs_file)))
            my_command = "vips dzsave " + my_file + " " + os.path.join(svs_files_dir2,
                                                                       svs_filename) + " --background 0 " + "--centre --layout dz"
            print(my_command)
            os.system(
                my_command
            )

    return 0


def tag_all_images():
    session_id = create_session()

    tcga_label2tag = {
        '1': 'idh1_present',
        '0': 'idh1_absent'
    }

    tcga_labels = get_tcga_labels()
    label_1_dir = os.path.join(svs_files_dir, 'idh1_present')
    if not os.path.exists(label_1_dir):
        os.makedirs(label_1_dir)
    label_0_dir = os.path.join(svs_files_dir, 'idh1_absent')
    if not os.path.exists(label_0_dir):
        os.makedirs(label_0_dir)

    for svs_file in get_imgfiles(svs_files_dir):
        svs_filename = os.path.basename(svs_file).split(".")[0]
        tcga_id = _svs_fname2tcga_id(svs_filename)
        outdir = os.path.join(svs_files_dir, svs_filename + '_files', str(zoom_level))
        if os.path.exists(outdir):
            image_list = img_files_to_s3_urls(get_imgfiles(outdir))
            # only add image to dataset if there is enough tissue
            filtered_image_list = handle_pathology(image_list)

            for img_url in filtered_image_list:
                my_tag = tcga_label2tag[tcga_labels[tcga_id]]
                print(tag_image(session_id, my_tag, img_url))

    return session_id

def prepare_dataset():
    label_1_dir = os.path.join(svs_files_dir, 'idh1_present')
    if not os.path.exists(label_1_dir):
        os.makedirs(label_1_dir)
    label_0_dir = os.path.join(svs_files_dir, 'idh1_absent')
    if not os.path.exists(label_0_dir):
        os.makedirs(label_0_dir)

    for img_file in get_imgfiles(label_0_dir):
        print(img_file)
        image_list = img_files_to_s3_urls([img_file])
        # only add image to dataset if there is enough tissue on the slide
        filtered_image_list = handle_pathology(image_list)
        if len(filtered_image_list) == 0:
            move(img_file, os.path.join(label_0_dir, 'background'))
            continue


if __name__ == '__main__':
    create_dz_files(get_imgfiles(svs_files_dir))
