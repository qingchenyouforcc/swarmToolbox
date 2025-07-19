from multiprocessing import process
import re
from loguru import logger
from pathlib import Path
import os
import subprocess
import psutil

# 导入win32api用于直接调用Windows系统命令
if os.name == 'nt':
    try:
        import win32api
        import win32con
        import win32process
    except ImportError:
        logger.warning("警告: win32api模块未安装，将使用备选启动方式")
        logger.warning("请安装pywin32: pip install pywin32")


def start_exe(path) -> bool:
    """启动exe。
    
    启动指定路径的exe程序
    支持多系统处理，Windows使用win32api启动，其他系统使用nohup
    
    Parameters:
        path: str
    
    Returns:
        bool: 成功启动返回True，失败返回False
    """
    if not path:
        logger.error("路径未设置")
        return False

    file = Path(path)

    # 检查文件是否存在
    if not file.exists():
        logger.error(f"文件不存在: {path}")
        return False

    # 检查是否为可执行文件
    if not file.suffix.lower() == '.exe':
        logger.error(f"文件不是可执行文件: {path}")
        return False

    try:
        # 使用win32api.ShellExecute启动，确保完全独立
        logger.info(f"正在启动程序: {path}")

        if os.name == 'nt':
            try:
                creation_flags = (
                        win32con.CREATE_NEW_PROCESS_GROUP |
                        win32con.DETACHED_PROCESS |
                        0x01000000  # CREATE_BREAKAWAY_FROM_JOB
                )

                # 准备启动信息
                startup_info = win32process.STARTUPINFO()
                startup_info.dwFlags = win32con.STARTF_USESHOWWINDOW
                startup_info.wShowWindow = win32con.SW_NORMAL

                # 创建进程
                process_info = win32process.CreateProcess(
                    None,  # 应用程序名（None表示从命令行获取）
                    f'"{str(file)}"',  # 命令行（程序路径）
                    None,  # 进程安全属性
                    None,  # 线程安全属性
                    False,  # 不继承句柄
                    creation_flags,  # 创建标志
                    None,  # 环境变量（None表示继承）
                    str(file.parent),  # 工作目录
                    startup_info  # 启动信息
                )

                # 立即关闭进程和线程句柄，完全断开关系
                win32api.CloseHandle(process_info[0])  # 进程句柄
                win32api.CloseHandle(process_info[1])  # 线程句柄

                logger.info(f"程序已通过CreateProcess独立启动，PID: {process_info[2]}")

            # Note: ImportError is already handled at the module level.
            except Exception as e:
                logger.error(f"CreateProcess启动失败: {e}")
                return False
        else:
            # 非Windows系统使用nohup
            nohup_path = os.path.join(file.parent, "nohup.out")
            process = subprocess.Popen(
                f"nohup {str(file)} > {nohup_path} 2>&1 &",
                cwd=str(file.parent),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
            logger.info(f"程序已通过nohup启动, PROCESS: {process}")

        return True

    except FileNotFoundError:
        logger.error(f"找不到可执行文件: {path}")
        return False
    except PermissionError:
        logger.error(f"没有权限执行文件: {path}")
        return False
    except Exception as e:
        logger.error(f"启动程序失败: {e}")
        return False


def start_exe_blocking(path) -> tuple[bool, str]:
    """启动exe并等待执行完成。
    
    启动指定的exe程序并等待执行完成；五分钟超时
    
    Parameters:
        path: str
    
    Returns:
        result: tuple[bool, str]: (是否成功, 输出信息)
    """
    if not path:
        return False, "exe路径未设置"

    file = Path(path)

    if not file.exists():
        return False, f"exe文件不存在: {path}"

    try:
        logger.info(f"正在启动程序: {path}")
        result = subprocess.run(
            [str(file)],
            cwd=str(file.parent),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            logger.info("程序执行成功")
            return True, result.stdout
        else:
            logger.error(f"程序执行失败，返回码: {result.returncode}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        logger.error("程序执行超时")
        return False, "程序执行超时"
    except Exception as e:
        logger.error(f"启动程序失败: {e}")
        return False, str(e)


def get_folder_size(path) -> tuple[bool, str]:
    """获取当前应用路径下文件夹空间占用情况。
    
    支持获取指定应用路径下的文件夹大小，自带单位转换
    
    Parameters:
        path: str
    
    Returns:
        result: tuple[bool, str]: (是否成功, 大小信息)
    """
    if not path:
        return False, "路径未设置"

    file = Path(path)
    if not file.exists():
        return False, f"文件不存在: {path}"

    try:
        folder = file.parent
        total_size = 0
        file_count = 0

        # 遍历文件夹计算大小
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                    file_count += 1
                except (OSError, PermissionError):
                    continue

        # 转换为可读格式
        def format_size(size_bytes):
            """将字节数转换为可读格式"""
            if size_bytes == 0:
                return "0 B"
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_names[i]}"

        formatted_size = format_size(total_size)
        folder_info = f"文件夹: {folder.name}\n路径: {folder}\n总大小: {formatted_size}\n文件数量: {file_count}"

        logger.info(f"文件夹大小: {formatted_size}, 文件数: {file_count}")
        return True, folder_info

    except Exception as e:
        error_msg = f"获取文件夹大小失败: {e}"
        logger.error(error_msg)
        return False, error_msg


def get_exe_version(path) -> tuple[bool, str]:
    """检查应用程序版本号。
    
    支持多种检查方式和多系统处理
    
    返回版本信息为版本号
    
    如果无法获取版本信息，则返回文件大小
    
    Parameters:
        path: str
    
    Returns:
        result: tuple[bool, str]: (是否成功, 版本信息)
    """
    if not path:
        return False, "路径未设置"

    file = Path(path)
    if not file.exists():
        return False, f"文件不存在: {path}"

    try:
        # 尝试获取文件版本信息 方法1 (Windows)
        if os.name == 'nt':
            try:
                import win32api
                info = win32api.GetFileVersionInfo(str(file), "\\")
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{(ms >> 16) & 0xFFFF}.{ms & 0xFFFF}.{(ls >> 16) & 0xFFFF}.{ls & 0xFFFF}"
                logger.info(f"版本: {version}")
                return True, version

            except ImportError:
                logger.warning("win32api未安装，使用备选方法")
            except Exception as e:
                logger.warning(f"获取Windows版本信息失败: {e}")

        # 方法2: 尝试运行程序获取版本信息
        try:
            result = subprocess.run(
                [str(file), '--version'],
                capture_output=True,
                text=True,
                timeout=3  # 减少超时时间
            )
            if result.returncode == 0 and result.stdout.strip():
                version_info = f"{result.stdout.strip()}"
                return True, version_info
        except subprocess.TimeoutExpired:
            logger.warning("版本检查超时")
        except Exception:
            pass

        # 方法3: 尝试其他版本参数（跳过可能有问题的参数）
        for version_arg in ['-v']:  # 只尝试简单的参数
            try:
                result = subprocess.run(
                    [str(file), version_arg],
                    capture_output=True,
                    text=True,
                    timeout=2  # 更短的超时时间
                )
                if result.stdout and ('version' in result.stdout.lower() or 'v' in result.stdout.lower()[:10]):
                    version_info = f"{result.stdout.strip()[:200]}"
                    return True, version_info
            except Exception as e:
                logger.warning(f"[方法三]获取版本信息失败: {e}")
                continue

        # 方法4: 返回文件基本信息
        file_stat = file.stat()
        file_size = file_stat.st_size / 1024 / 1024  # MB
        size += f"{file_size:.2f} MB\n"

        logger.info("无法获取版本信息，返回文件大小")
        return True, size

    except Exception as e:
        error_msg = f"检查版本失败: {e}"
        logger.error(error_msg)
        return False, error_msg


def check_exe_running(path) -> bool:
    """检查程序是否正在运行。
    
    检查指定路径的程序是否正在运行
    支持多系统处理
    
    Parameters:
        path: str
    
    Returns:
        bool: 正在运行返回True
    """
    process = path.rsplit('/', 1)[-1] or path.rsplit('\\', 1)[-1]
    try:
        # 在Windows上检查进程
        if os.name == 'nt':
            result = subprocess.run(
                ['tasklist', '/FI', f"IMAGENAME eq {process}"],
                capture_output=True,
                text=True
            )
            return f'{process}' in result.stdout
        else:
            # Linux/Mac
            result = subprocess.run(
                ['pgrep', '-f', f'{process.rsplit(".exe")[0]}'],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
    except Exception as e:
        logger.error(f"检查进程失败: {e}")
        return False


def get_exe_usage(path, name="") -> tuple[bool, list[str]]:
    """获取进程资源占用情况。
    
    使用路径exe文件名称查找进程，并返回进程的资源占用情况。
    
    包括CPU使用率、内存使用情况等。
    
    你可以添加第二个参数name来指定查找的进程名
    
    Parameters:
        path: str
        name: str = ""  # 可选参数，用于指定进程名
    
    Returns:
        result: 
        tuple[bool, list[str]] (是否成功, 占用情况)
        
        其中list[str]:[概述，内存占用大小(自带单位), CPU使用率(%)]
    """
    try:
        processes = []
        process = path.rsplit('/', 1)[-1] or path.rsplit('\\', 1)[-1]

        # 查找相关进程
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if f"{process.rsplit(".exe")[0]}" in proc.info['name'] or f"{process.rsplit(".exe")[0]}".lower() in \
                        proc.info['name'].lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not processes:
            try:
                if name in proc.info['name']:
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            return False, "未找到进程"

        memory_info = []
        total_memory = 0
        total_cpu = 0

        for proc in processes:
            try:
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024  # 转换为MB
                cpu_percent = proc.cpu_percent()
                total_memory += memory_mb
                total_cpu += cpu_percent

                proc_info = f"内存占用: {memory_mb:.2f} MB\n"
                proc_info += f"CPU使用率: {cpu_percent:.1f}%"

                memory_info.append(proc_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        usage_info = []

        if memory_info:
            result = f"找到 {len(processes)} 个NSP进程\n"
            result += f"总内存占用: {total_memory:.2f} MB\n\n"
            logger.info(f"进程内存占用: {total_memory:.2f} MB")
            result += f"总CPU使用率: {total_cpu:.1f}%\n"
            logger.info(f"进程CPU使用率: {total_cpu:.1f}%")
            result += "\n" + "=" * 40 + "\n" + "".join(memory_info)

            usage_info.append(result)
            usage_info.append(total_memory)
            usage_info.append(total_cpu)

            return True, usage_info
        else:
            return False, "无法获取进程信息"

    except Exception as e:
        error_msg = f"获取内存使用情况失败: {e}"
        logger.error(error_msg)
        return False, error_msg
