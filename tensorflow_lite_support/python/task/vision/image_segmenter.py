# Copyright 2022 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Image segmenter task."""

import dataclasses
from typing import Optional

from tensorflow_lite_support.python.task.core.proto import base_options_pb2
from tensorflow_lite_support.python.task.processor.proto import segmentation_options_pb2
from tensorflow_lite_support.python.task.processor.proto import segmentations_pb2
from tensorflow_lite_support.python.task.vision.core import tensor_image
from tensorflow_lite_support.python.task.vision.core.pybinds import image_utils
from tensorflow_lite_support.python.task.vision.pybinds import _pywrap_image_segmenter

_OutputType = segmentation_options_pb2.OutputType
_CppImageSegmenter = _pywrap_image_segmenter.ImageSegmenter
_BaseOptions = base_options_pb2.BaseOptions


@dataclasses.dataclass
class ImageSegmenterOptions:
  """Options for the image segmenter task."""
  base_options: _BaseOptions
  segmentation_options: Optional[
      segmentation_options_pb2.SegmentationOptions] = None


class ImageSegmenter(object):
  """Class that performs segmentation on images."""

  def __init__(self, options: ImageSegmenterOptions,
               segmenter: _CppImageSegmenter) -> None:
    """Initializes the `ImageSegmenter` object."""
    # Creates the object of C++ ImageSegmenter class.
    self._options = options
    self._segmenter = segmenter

  @classmethod
  def create_from_file(cls, file_path: str) -> "ImageSegmenter":
    """Creates the `ImageSegmenter` object from a TensorFlow Lite model.

    Args:
      file_path: Path to the model.
    Returns:
      `ImageSegmenter` object that's created from `options`.
    Raises:
      RuntimeError if failed to create `ImageSegmenter` object from the provided
        file such as invalid file.
    """
    base_options = _BaseOptions(file_name=file_path)
    options = ImageSegmenterOptions(base_options=base_options)
    return cls.create_from_options(options)

  @classmethod
  def create_from_options(cls,
                          options: ImageSegmenterOptions) -> "ImageSegmenter":
    """Creates the `ImageSegmenter` object from image segmenter options.

    Args:
      options: Options for the image segmenter task.
    Returns:
      `ImageSegmenter` object that's created from `options`.
    Raises:
      RuntimeError if failed to create `ImageSegmenter` object from
        `ImageSegmenterOptions` such as missing the model.
    """
    segmenter = _CppImageSegmenter.create_from_options(
        options.base_options, options.segmentation_options)
    return cls(options, segmenter)

  def segment(
      self,
      image: tensor_image.TensorImage
  ) -> segmentations_pb2.SegmentationResult:
    """Performs segmentation on the provided TensorImage.

    Args:
      image: Tensor image, used to extract the feature vectors.
    Returns:
      segmentation result.
    Raises:
      RuntimeError if failed to get the segmentation result.
    """
    image_data = image_utils.ImageData(image.buffer)
    return self._segmenter.segment(image_data)
