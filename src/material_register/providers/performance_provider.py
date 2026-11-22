from datetime import datetime
from time import perf_counter

from material_register.providers.logger_provider import LoggerProvider


class PerformanceProvider:
    @staticmethod
    def start() -> float:
        return perf_counter()

    @staticmethod
    def stop(start_time: float, section: str, comment: str = "") -> None:
        elapsed = perf_counter() - start_time
        if elapsed < 1:
            duration = f"{elapsed * 1000:.2f} ms"
        else:
            duration = f"{elapsed:.2f} s"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if comment:
            section += f" - {comment}"
        performance = f"{current_time} | {section} | {duration}"
        LoggerProvider.performance.info(performance)
