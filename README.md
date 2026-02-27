Acoustic Dataset Preparation for Industrial Fault Detection

This repository contains Python scripts developed for dataset preparation within the research project “Methodology for Creating an Acoustic Classifier Based on Neural Networks for Industrial Equipment Diagnostics.”

The overall research project focuses on building a complete methodology for designing an acoustic classification system capable of detecting industrial equipment faults using neural networks.

Important: This repository includes only dataset preparation tools. Neural network architecture, trained models, inference pipeline, real-time processing system, and deployment components are not included due to commercial confidentiality.

The purpose of this repository is to provide a structured, reproducible, and scalable pipeline for preparing industrial acoustic data for machine learning tasks. The scripts implement audio preprocessing, resampling to 16 kHz, mono channel normalization, segmentation of long recordings into fixed-length samples, label processing (including JSON-based annotations such as Label Studio exports), dataset structuring, metadata generation, and stratified train/validation/test splitting without data leakage. The pipeline also supports basic augmentation techniques such as gain adjustment, noise mixing, and time shifting, and prepares data for spectrogram-based deep learning models.

The methodology was developed as part of a broader acoustic monitoring system that includes data collection, manual and semi-automatic labeling, mel-spectrogram generation, CNN-based classification, model optimization (including quantization and pruning), and deployment on edge devices such as Raspberry Pi. The target application of the full system is industrial fault detection through acoustic anomaly recognition.

The dataset preparation workflow includes the following stages:

Audio standardization (conversion to mono, resampling to 16 kHz, format normalization, and structured directory organization).

Label processing and metadata structuring.

Segmentation of long recordings into fixed-duration samples while preserving label alignment.

Stratified dataset splitting into training, validation, and test sets without cross-contamination.

Optional augmentation-ready preparation for improving model robustness.

The technical stack used in this repository includes Python 3, NumPy, Librosa, SoundFile, and JSON-based label handling. While PyTorch is used in the broader research project, model-related code is intentionally excluded from this repository.

For commercial confidentiality reasons, the following components are not included: neural network architecture implementation, training pipeline, trained weights, optimized edge inference code, real-time monitoring logic, and deployment scripts. This repository serves exclusively as a demonstration of the data engineering and preprocessing methodology developed within the research project.

The dataset preparation pipeline is modular, reproducible, and adaptable for other acoustic classification tasks with minimal modification.

Author: Mark Smertenko
Research Project – Acoustic Industrial Fault Detection
Kyiv, 2026
