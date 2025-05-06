# EAEFNet

![license](https://img.shields.io/badge/license-MIT-green) ![PyTorch-1.10.0](https://img.shields.io/badge/PyTorch-1.10.0-blue)



## 环境安装

```shell
conda create -n EAEF python=3.8 pytorch==1.10.1 torchvision==0.11.2 cudatoolkit=11.3 -c pytorch -y
conda activate EAEF
pip install openmim
mim install "mmengine>=0.3.1"
mim install "mmcv>=2.0.0rc1,<2.1.0"
mim install "mmdet>=3.0.0rc3,<3.1.0"
cd EAEFNet_Detection/EAEF_mmyolo
# Install albumentations
pip install -r requirements/albu.txt
# Install MMYOLO , don't forget it!
mim install -v -e .
```

## 单卡训练
```
CUDA_VISIBLE_DEVICES=0 python ./EAEF_mmyolo/tools/train.py --config ./EAEF_mmyolo/configs/yolov5/bi_yolov5-OdinMJ-coco.py
```
## 多卡训练

```
CUDA_VISIBLE_DEVICES=0,1,2,3 PORT=29500 nohup bash ./tools/dist_train.sh --config ./EAEF_mmyolo/configs/yolov5/bi_yolov5-OdinMJ-coco.py
```

## 载入checkpoint测试

```
CUDA_VISIBLE_DEVICES=0 python ./EAEF_mmyolo/tools/test.py --config ./EAEF_mmyolo/configs/yolov5/bi_yolov5-OdinMJ-coco.py --checkpoint ./work_dirs/checkpoints/20240322_113553/bi_yolov5-OdinMj-coco/best_coco_bbox_mAP_epoch_7.pth
```

