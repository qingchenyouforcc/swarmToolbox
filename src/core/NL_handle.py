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


def set_nl_path(path: str) -> None:
    """设置Neurolings文件路径"""
    cfg.neurolings_path.value = path
    cfg.save()
    logger.info(f"Neurolings路径已设置为: {path}")
    
if __name__ == "__main__":
    # 测试用例
    test_path = r"C:\The-Neuroling-Collection\Neurolings.exe"

    # 设置路径
    set_nl_path(test_path)
    print(f"当前Neurolings路径: {cfg.neurolings_path.value}")

    Neurolings_file = Path(test_path)
    if Neurolings_file.exists():
        print("\n" + "=" * 50)
        print("🔍 进程状态检查:")
        try:
            user_input = input("是否启动Neurolings程序? (y/N): ").strip().lower()
            if user_input in ['y', 'yes', '是']:
                if start_exe(test_path):
                    print("✅ Neurolings程序启动成功")
                    # Neurolings程序启动后，会启动javaw.exe
                    # 因为javaw.exe涉及程序太多，无法进行占用反馈和运行判断
                else:
                    print("❌ Neurolings程序启动失败")
            else:
                print("已取消启动")
        except KeyboardInterrupt:
            print("\n\n已中断操作")
    else:
        print("❌ Neurolings文件不存在，请检查路径")

    print("\n" + "=" * 50)