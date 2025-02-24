import asyncio
from pathlib import Path
from typing import Iterable

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from universalasync import async_to_sync_wraps

from Domain.SDFHandler import SDFHandler
from Domain.logger.OTLLogger import OTLLogger
from GUI.dialog_windows.LoadingImageWindow import add_loading_screen


class ConverterHelper:

    @classmethod
    @async_to_sync_wraps
    async def converter_from_file_to_object(cls, file_path, **kwargs):

        if isinstance(file_path,str):
            file_path = Path(file_path)

        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        exception_group = None
        object_count = 0
        try:
            object_lists = list(await OtlmowConverter.from_file_to_objects(file_path, **kwargs))
        except ExceptionsGroup as group:
            exception_group = group
            object_lists = group.objects

        object_count = len(object_lists)
        OTLLogger.logger.debug(
            f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({object_count} objects)",
            extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        return object_lists, exception_group

    @classmethod
    def start_async_converter_from_object_to_file(cls, file_path: Path,
                                                  sequence_of_objects: Iterable[OTLObject],
                                                  synchronous: bool = False, **kwargs) -> None:

        if not synchronous:
            if (file_path.suffix == ".sdf"):
                event_loop = asyncio.get_event_loop()
                event_loop.create_task(SDFHandler.convert_object_to_SDF_file(object_list=list(sequence_of_objects),
                                                                             output_sdf_path=file_path))
            else:
                event_loop = asyncio.get_event_loop()
                event_loop.create_task(cls.converter_from_object_to_file(file_path=file_path,
                                                                        sequence_of_objects=sequence_of_objects,
                                                                        **kwargs))
        else:
            if (file_path.suffix == ".sdf"):
                SDFHandler.convert_object_to_SDF_file(file_path=file_path,
                                                      sequence_of_objects=sequence_of_objects,
                                                      **kwargs)
            else:
                cls.converter_from_object_to_file(object_list=list(sequence_of_objects),
                                                  output_sdf_path=file_path)

    @classmethod
    @async_to_sync_wraps
    @add_loading_screen
    async def converter_from_object_to_file(cls, file_path: Path,
                                            sequence_of_objects: Iterable[OTLObject],
                                            **kwargs) -> None:
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_objects_to_file({file_path.name})",
                               extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})
        await OtlmowConverter.from_objects_to_file(file_path=file_path,
                                                   sequence_of_objects=sequence_of_objects,
                                                   **kwargs)
        object_count = len(list(sequence_of_objects))
        OTLLogger.logger.debug(
            f"Execute OtlmowConverter.from_objects_to_file({file_path.name}) ({object_count} objects)",
            extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})