default_scope = 'mmyolo'
default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='LoggerHook', interval=1),
    param_scheduler=dict(
        type='YOLOv5ParamSchedulerHook',
        scheduler_type='linear',
        lr_factor=0.01,
        max_epochs=300),
    checkpoint=dict(
        type='CheckpointHook', interval=10, save_best='auto',
        max_keep_ckpts=3),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    visualization=dict(
        type='mmdet.DetVisualizationHook',
        draw=True,
        test_out_dir='./show_results'))
env_cfg = dict(
    cudnn_benchmark=True,
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0),
    dist_cfg=dict(backend='nccl'))
vis_backends = [dict(type='LocalVisBackend')]
visualizer = dict(
    type='mmdet.DetLocalVisualizer',
    vis_backends=[dict(type='LocalVisBackend')],
    name='visualizer')
log_processor = dict(type='LogProcessor', window_size=50, by_epoch=True)
log_level = 'INFO'
load_from = './model_hub/yolov5_m-v61_syncbn_fast_8xb16-300e_coco_20220917_204944-516a710f.pth'
resume = False
file_client_args = dict(backend='disk')
data_root = './EAEFNet/EAEFNet_Detection/EAEF_mmyolo/data'
dataset_type = 'YOLOv5CocoDataset'
num_classes = 6
img_scale = (640, 640)
deepen_factor = 0.67
widen_factor = 0.75
max_epochs = 300
save_epoch_intervals = 10
train_batch_size_per_gpu = 4
train_num_workers = 2
val_batch_size_per_gpu = 1
val_num_workers = 2
persistent_workers = True
batch_shapes_cfg = dict(
    type='BatchShapePolicy',
    batch_size=1,
    img_size=640,
    size_divisor=32,
    extra_pad_ratio=0.5)
anchors = [[(10, 13), (16, 30), (33, 23)], [(30, 61), (62, 45), (59, 119)],
           [(116, 90), (156, 198), (373, 326)]]
strides = [8, 16, 32]
num_det_layers = 3
model = dict(
    type='YOLODetector',
    data_preprocessor=dict(
        type='YOLOv5DetDataPreprocessor',
        mean=[0.0,0.0,0.0,0.0],
        std=[255.0,255.0,255.0,255.0],
        bgr_to_rgb=True),
    backbone=dict(
        type='BiYOLOv5CSPDarknet',
        deepen_factor=0.67,
        widen_factor=0.75,
        norm_cfg=dict(type='BN', momentum=0.03, eps=0.001),
        act_cfg=dict(type='SiLU', inplace=True)),
    neck=dict(
        type='YOLOv5PAFPN',
        deepen_factor=0.67,
        widen_factor=0.75,
        in_channels=[256, 512, 1024],
        out_channels=[256, 512, 1024],
        num_csp_blocks=3,
        norm_cfg=dict(type='BN', momentum=0.03, eps=0.001),
        act_cfg=dict(type='SiLU', inplace=True)),
    bbox_head=dict(
        type='YOLOv5Head',
        head_module=dict(
            type='YOLOv5HeadModule',
            num_classes=6,
            in_channels=[256, 512, 1024],
            widen_factor=0.75,
            featmap_strides=[8, 16, 32],
            num_base_priors=3),
        prior_generator=dict(
            type='mmdet.YOLOAnchorGenerator',
            base_sizes=[[(10, 13), (16, 30), (33, 23)],
                        [(30, 61), (62, 45), (59, 119)],
                        [(116, 90), (156, 198), (373, 326)]],
            strides=[8, 16, 32]),
        loss_cls=dict(
            type='mmdet.CrossEntropyLoss',
            use_sigmoid=True,
            reduction='mean',
            loss_weight=0.3),
        loss_bbox=dict(
            type='IoULoss',
            iou_mode='ciou',
            bbox_format='xywh',
            eps=1e-07,
            reduction='mean',
            loss_weight=0.05,
            return_iou=True),
        loss_obj=dict(
            type='mmdet.CrossEntropyLoss',
            use_sigmoid=True,
            reduction='mean',
            loss_weight=0.7),
        prior_match_thr=4.0,
        obj_level_weights=[4.0, 1.0, 0.4]),
    test_cfg=dict(
        multi_label=True,
        nms_pre=30000,
        score_thr=0.001,
        nms=dict(type='nms', iou_threshold=0.65),
        max_per_img=300))

train_dataloader = dict(
    batch_size=4,
    num_workers=2,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type='YOLOv5CocoDataset',
        data_root='./EAEFNet/EAEFNet_Detection/EAEF_mmyolo/data',
        data_prefix=dict(img='train/'),
        ann_file='instances_train2014.json',
        filter_cfg=dict(filter_empty_gt=False, min_size=32),
        pipeline=[
            dict(type='LoadImage'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(
                type='Mosaic',
                img_scale=(640, 640),
                pad_val=114.0,
                pre_transform=[
                    dict(type='LoadImage'),
                    dict(type='LoadAnnotations', with_bbox=True)
                ]),
            dict(
                type='YOLOv5RandomAffine',
                max_rotate_degree=0.0,
                max_shear_degree=0.0,
                scaling_ratio_range=(0.5, 1.5),
                border=(-320, -320),
                border_val=(114, 114, 114)),
            dict(
                type='mmdet.Albu',
                transforms=[
                    dict(type='Blur', p=0.01),
                    dict(type='MedianBlur', p=0.01)
                ],
                bbox_params=dict(
                    type='BboxParams',
                    format='pascal_voc',
                    label_fields=['gt_bboxes_labels', 'gt_ignore_flags']),
                keymap=dict(img='image', gt_bboxes='bboxes')),

            dict(type='mmdet.RandomFlip', prob=0.5),
            dict(
                type='mmdet.PackDetInputs',
                meta_keys=('img_id', 'img_path', 'ori_shape', 'img_shape',
                           'flip', 'flip_direction'))
        ],
        metainfo=dict(
            classes=('Car', 'Truck', 'People', 'Bus', 'Lamp', 'Motorcycle'),
            palette=[(220, 20, 60), (255, 0, 255), (0, 255, 255), (0, 0, 255),
                     (183, 43, 42), (123, 23, 32)])))
collate_fn=dict(type='yolov5_collate')

val_dataloader = dict(
    batch_size=1,
    num_workers=2,
    persistent_workers=True,
    pin_memory=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='YOLOv5CocoDataset',
        data_root='./EAEFNet/EAEFNet_Detection/EAEF_mmyolo/data',
        test_mode=True,
        data_prefix=dict(img='val/'),
        ann_file='instances_val2014.json',
        pipeline=[
            dict(type='LoadImage'),
            dict(type='YOLOv5KeepRatioResize', scale=(640, 640)),
            dict(
                type='LetterResize',
                scale=(640, 640),
                allow_scale_up=False,
                pad_val=dict(img=114)),
            dict(type='LoadAnnotations', with_bbox=True, _scope_='mmdet'),
            dict(
                type='mmdet.PackDetInputs',
                meta_keys=('img_id', 'img_path', 'ori_shape', 'img_shape',
                           'scale_factor', 'pad_param'))
        ],
        batch_shapes_cfg=dict(
            type='BatchShapePolicy',
            batch_size=1,
            img_size=640,
            size_divisor=32,
            extra_pad_ratio=0.5),
        metainfo=dict(
            classes=('Car', 'Truck', 'People', 'Bus', 'Lamp', 'Motorcycle'),
            palette=[(220, 20, 60), (255, 0, 255), (0, 255, 255), (0, 0, 255),
                     (183, 43, 42), (123, 23, 32)])))

test_dataloader = val_dataloader

param_scheduler = None
optim_wrapper = dict(
    type='OptimWrapper',
    optimizer=dict(
        type='SGD',
        lr=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        nesterov=True,
        batch_size_per_gpu=16),
    constructor='YOLOv5OptimizerConstructor')

custom_hooks = [
    dict(
        type='EMAHook',
        ema_type='ExpMomentumEMA',
        momentum=0.0001,
        update_buffers=True,
        strict_load=False,
        priority=49)
]
val_evaluator = dict(
    type='mmdet.CocoMetric',
    proposal_nums=(100, 1, 10),
    ann_file='./EAEFNet/EAEFNet_Detection/EAEF_mmyolo/data/instances_val2014.json',
    metric='bbox')

test_evaluator = dict(
    type='mmdet.CocoMetric',
    proposal_nums=(100, 1, 10),
    ann_file='./EAEFNet/EAEFNet_Detection/EAEF_mmyolo/data/instances_val2014.json',
    metric='bbox')
train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=400, val_interval=10)
val_cfg = dict(type='ValLoop')
test_cfg = dict(type='TestLoop')
metainfo=dict(
        classes=('Car', 'Truck', 'People', 'Bus', 'Lamp', 'Motorcycle'),
        palette=[(220, 20, 60), (255, 0, 255), (0, 255, 255), (0, 0, 255),
                     (183, 43, 42), (123, 23, 32)])

vis_backends = [dict(type='LocalVisBackend')]
# visualizer = dict(
#     type='mmdet.DetLocalVisualizer',
#     vis_backends=[dict(type='LocalVisBackend'),
#                   dict(type='WandbVisBackend')],
#     name='visualizer')

launcher = 'none'
work_dir = './work_dirs/bi_idam_yolov5'
