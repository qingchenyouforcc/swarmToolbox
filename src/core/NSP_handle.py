from pathlib import Path
from loguru import logger

import sys

# 智能路径处理：支持直接运行和模块导入

try:
    from src.config import cfg
    from src.utils.file_system_utils import (
        start_exe, check_exe_running)
except ModuleNotFoundError:
    # 如果导入失败，添加项目根目录到sys.path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.config import cfg
    from src.utils.file_system_utils import (
        start_exe, check_exe_running, get_exe_usage)


def set_nsp_path(path: str) -> None:
    """设置NSP文件路径"""
    cfg.nsp_path.value = path
    cfg.save()
    logger.info(f"NSP路径已设置为: {path}")


if __name__ == "__main__":
    # 测试用例
    test_path = "C:/neuroSangSpider/NeuroSongSpider.exe"
    print("=== NSP处理器测试 ===")

    # 设置路径
    set_nsp_path(test_path)
    print(f"当前NSP路径: {cfg.nsp_path.value}")

    nsp_file = Path(test_path)
    if nsp_file.exists():
        print("\n" + "=" * 50)
        print("🔍 进程状态检查:")
        if check_exe_running(test_path):
            print("⚠️  NSP程序已在运行")

            print("\n📊 内存占用情况:")
            success, memory_info = get_exe_usage(test_path)
            if success:
                print(memory_info[0])
                print(memory_info[1])
                print(memory_info[2])
            else:
                print(f"❌ {memory_info}")
        else:
            print("ℹ️  NSP程序未运行")

            try:
                user_input = input("是否启动NSP程序? (y/N): ").strip().lower()
                if user_input in ['y', 'yes', '是']:
                    if start_exe(test_path):
                        print("✅ NSP程序启动成功")

                        import time

                        print("等待3秒后检查内存占用...")
                        time.sleep(3)

                        success, memory_info = get_exe_usage(test_path)
                        if success:
                            print("\n📊 启动后内存占用:")
                            print(memory_info[0])
                            print(memory_info[1])
                            print(memory_info[2])
                    else:
                        print("❌ NSP程序启动失败")
                else:
                    print("已取消启动")
            except KeyboardInterrupt:
                print("\n\n已中断操作")
    else:
        print("❌ NSP文件不存在，请检查路径")

    print("\n" + "=" * 50)

    # 如果NSP已经成功启动，提示用户可以关闭脚本
    if check_exe_running(test_path):
        print("✅ NSP程序已成功启动并正在运行！")
