from pathlib import Path
from loguru import logger
import sys
import time

# 智能路径处理：支持直接运行和模块导入

try:
    from src.config import cfg
    from src.utils.file_system_utils import (
        check_exe_running, get_exe_usage, kill_exe, start_exe_used_bat)
except ModuleNotFoundError:
    # 如果导入失败，添加项目根目录到sys.path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.config import cfg
    from src.utils.file_system_utils import (
        check_exe_running, get_exe_usage, kill_exe, start_exe_used_bat)


def set_evz_path(path: str) -> None:
    """设置evz文件路径"""
    cfg.evz_path.value = path
    cfg.save()
    logger.info(f"evz路径已设置为: {path}")


def start_evz(path: str) -> bool:
    """启动evz程序"""
    bat_content = f"""
        @echo off

        set "app={path}"

        :: 添加兼容性设置
        reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%app%" /d "~ 16BITCOLOR" /f

        :: 启动应用程序
        start "" "%app%"
    """
    return start_exe_used_bat(path, bat_content)

    
if __name__ == "__main__":
    # 测试用例
    test_path = r"D:\EVZ\EVZ1.4T24.exe"

    # 设置路径
    set_evz_path(test_path)
    print(f"当前evz路径: {cfg.evz_path.value}")

    evz_file = Path(test_path)
    if evz_file.exists():
        print("\n" + "=" * 50)
        print("🔍 进程状态检查:")
        if check_exe_running(test_path):
            print("⚠️  evz程序已在运行")

            print("\n📊 内存占用情况:")
            success, memory_info = get_exe_usage(test_path)
            if success:
                print(memory_info[0])
                print(memory_info[1])
                print(memory_info[2])
            else:
                print(f"❌ {memory_info}")
            
            # 添加结束进程选项
            try:
                user_input = input("\n是否结束evz程序? (y/N): ").strip().lower()
                if user_input in ['y', 'yes', '是']:
                    success, result_msg = kill_exe(test_path)
                    if success:
                        print(f"✅ {result_msg}")
                    else:
                        print(f"❌ {result_msg}")
                else:
                    print("已取消结束进程")
            except KeyboardInterrupt:
                print("\n\n已中断操作")
        else:
            print("ℹ️  evz程序未运行")

            try:
                user_input = input("是否启动evz程序? (y/N): ").strip().lower()
                if user_input in ['y', 'yes', '是']:
                    if start_evz(test_path):
                        print("✅ evz程序启动成功")

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
                        print("❌ evz程序启动失败")
                else:
                    print("已取消启动")
            except KeyboardInterrupt:
                print("\n\n已中断操作")
    else:
        print("❌ evz文件不存在，请检查路径")

    print("\n" + "=" * 50)

    # 如果evz已经成功启动，提示用户可以关闭脚本
    if check_exe_running(test_path):
        print("✅ evz程序已成功启动并正在运行！")