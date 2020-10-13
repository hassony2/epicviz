from collections import defaultdict, OrderedDict
from pathlib import Path
from tqdm import tqdm
from epic.smplifyx import optim_factory
from epic.egofit import egoviz


def fit_human(
    data,
    supervision,
    scene,
    egolosses,
    save_folder=Path("tmp"),
    iters=100,
    lr=0.1,
    optimizer="adam",
    optim_shape=False,
    viz_step=10,
    debug=False,
):
    scene.cuda()
    optim_params = scene.get_optim_params()
    print(f"Optimizing {len(optim_params)} parameters")
    optimizer, _ = optim_factory.create_optimizer(
        optim_params, optim_type=optimizer, lr=lr
    )

    losses = defaultdict(list)
    img_paths = OrderedDict()
    for iter_idx in tqdm(range(iters)):
        scene_outputs = scene.forward()
        if iter_idx % viz_step == 0:
            img_path = egoviz.ego_viz(
                data,
                supervision,
                scene_outputs,
                save_folder=save_folder / "viz",
                step_idx=iter_idx,
            )
            img_paths[iter_idx] = img_path
        loss, step_losses = egolosses.compute_losses(
            scene_outputs, supervision
        )
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if debug:
            print_losses = ", ".join(
                [f"{key}: {val:.2e}" for key, val in step_losses.items()]
            )
            print(f"Step losses: {print_losses}")
        metrics = egolosses.compute_metrics(scene_outputs, supervision)
        # Collect metrics
        for key, val in step_losses.items():
            losses[key].append(val)

        for key, val in metrics.items():
            losses[key].append(val)
    res = {"losses": dict(losses), "imgs": img_paths}
    return res
