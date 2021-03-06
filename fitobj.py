import argparse
from pathlib import Path

import pickle
from epic.fitting import fitobj

from libyana.exputils import argutils

parser = argparse.ArgumentParser()
parser.add_argument("--pickle_path", default="tmp.pkl")
parser.add_argument("--radius", default=0.1, type=float)
parser.add_argument("--z_offs", default=[0.3], type=float, nargs="+")
parser.add_argument("--viz_step", default=10, type=int)
parser.add_argument("--iters", default=100, type=int)
parser.add_argument("--lrs", default=[0.01], type=float, nargs="+")
parser.add_argument(
    "--loss_types",
    default=["adapt"],
    choices=["adapt", "l2", "l1", "adapt_dtf", "l2_dtf", "l1_dtf"],
    nargs="+",
)
parser.add_argument("--faces_per_pixels", default=[2], type=int, nargs="+")
parser.add_argument("--save_root", default="tmp")
parser.add_argument("--rot_nb", default=1, type=int)
parser.add_argument("--no_crop", action="store_true")
args = parser.parse_args()
argutils.print_args(args)

with open(args.pickle_path, "rb") as p_f:
    data = pickle.load(p_f)
masks = [dat["mask"] for dat in data]
bboxes = [dat["boxes"] for dat in data]
obj_paths = [dat["obj_path"] for dat in data]
for lr in args.lrs:
    for loss_type in args.loss_types:
        for z_off in args.z_offs:
            for faces_per_pixel in args.faces_per_pixels:
                save_folder = (
                    Path(args.save_root)
                    / f"lr{lr}_lt{loss_type}_zoff{z_off}_fpp{faces_per_pixel}"
                )
                res = fitobj.fitobj2mask(
                    masks,
                    bboxes,
                    obj_paths,
                    z_off=z_off,
                    radius=args.radius,
                    lr=lr,
                    viz_step=args.viz_step,
                    save_folder=save_folder,
                    loss_type=loss_type,
                    iters=args.iters,
                    faces_per_pixel=faces_per_pixel,
                    crop_box=not args.no_crop,
                    rot_nb=args.rot_nb,
                )
                with open(save_folder / "res.pkl", "wb") as p_f:
                    pickle.dump(res, p_f)
                print(f"Saved run info to {save_folder}")
