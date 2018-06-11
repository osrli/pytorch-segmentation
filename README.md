# segmentation
Implementation of various state-of-the-art segmentation methods

### Usage
#### Train model (without resume)
```bash
python main.py --gpu=1 --resume=0 --train=1 --evaluate=1 --checkpoints=./checkpoints/ --config=./experiments/config.yaml
```

#### Train model (with resume)
Download models from [here](https://github.com/osrli/segmentation). Place them in `./checkpoints` folder and mention the checkpoint to be loaded in the `config.yaml` file.

```bash
python main.py --gpu=1 --resume=1 --train=1 --evaluate=1 --checkpoints=./checkpoints/ --config=./experiments/config.yaml
```

#### Use Trained model
Download models from [here](https://github.com/osrli/segmentation). Place them in `./checkpoints` folder and mention the checkpoint to be loaded in the `config.yaml` file.

```bash
python main.py --gpu=1 --resume=1 --train=0 --evaluate=1 --checkpoints=./checkpoints/ --config=./experiments/config.yaml
```
