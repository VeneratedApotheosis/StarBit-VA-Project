from pipecat.frames.frames import Frame, LLMFullResponseEndFrame, TextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class TextPrinter(FrameProcessor):
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TextFrame):
            print(f"[TEXT]: {frame.text}")
        await self.push_frame(frame, direction)


class LLMResponsePrinter(FrameProcessor):
    def __init__(self):
        super().__init__()
        self._buffer = []

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TextFrame):
            self._buffer.append(frame.text)

        # print and clear buffer when LLM finishes generation
        elif isinstance(frame, LLMFullResponseEndFrame):
            full_text = "".join(self._buffer)
            print(f"[LLM OUTPUT]: {full_text}")
            self._buffer.clear()

        # pass the original frame downstream
        await self.push_frame(frame, direction)