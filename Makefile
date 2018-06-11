all: data main

data:
	bash data/download.sh

main:
	python main.py --gpu=1 --resume=0 --train=1 --evaluate=1 --checkpoints=./checkpoints/ --config=./experiments/config.yaml 

profile:
	python -m cProfile -s cumtime main.py --gpu=1 --resume=0 --checkpoints=./checkpoints/ --config=./experiments/config.yaml

mem_profile:
	python -m memory_profiler main.py --gpu=1 --resume=0 --checkpoints=./checkpoints/ --config=./experiments/config.yaml
