# MedGemma 1.5 Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/google/technical-reports/medgemma-1-5-technical-report--arxiv-v2.pdf) · [Official source](https://arxiv.org/abs/2604.05081)

## Overview · Figure 1

Source page: 2 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/google/technical-reports/medgemma-1-5-technical-report--arxiv-v2.pdf#page=2)

![Overview](figure-01.png)

Figure 1 | Overview of model capabilities within the MedGemma collection. The updated MedGemma
1.5 4B architecture now supports 3D radiology (CT/MRI volumes), pathology whole slide imaging (WSI),
anatomical localization, and multi-timepoint analysis. The original MedGemma 27B model remains available
for complex clinical knowledge and reasoning tasks and MedSigLIP remains available for medical image
classification and retrieval tasks.

## Results · Figure 2

Source page: 3 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/google/technical-reports/medgemma-1-5-technical-report--arxiv-v2.pdf#page=3)

![Results](figure-02.png)

Figure 2 | The left panel details accuracy on medical text Q&A tasks (MedQA and EHRQA), while the right panel highlights
performance across diverse medical imaging capabilities. Notably, the "medical image interpretation" score represents
an unweighted macro average of the model’s performance across 7 distinct imaging tasks including MIMIC-CXR (both
RadGraph F1 and report generation macro F1), CheXpert (unweighted average across 5 conditions), CXR 14 (unweighted
average across 3 conditions), Path MCQA, DermMCQA, and EyePACS. "Lab report extraction" is macro-averaged over results
from EHR dataset 2, 3 and 4 as well as Mendeley Clinical Laboratory Test Reports (macro F1). All scores are reported as
percentages. While the out-of-the-box performance is highly promising, the model is not meant to be deployed without the
necessary clinical fine-tuning. Fine-tuning may improve results and adapt the framework for practical use.
