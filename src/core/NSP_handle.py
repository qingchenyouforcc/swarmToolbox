from pathlib import Path
from loguru import logger

import psutil  
import subprocess
import os
import sys

# 导入win32api用于直接调用Windows系统命令
if os.name == 'nt':
    try:
        import win32api
        import win32con
        import win32process
    except ImportError:
        print("警告: win32api模块未安装，将使用备选启动方式")
        print("请安装pywin32: pip install pywin32")

# 智能路径处理：支持直接运行和模块导入

try:
    from src.config import cfg
except ModuleNotFoundError:
    # 如果导入失败，添加项目根目录到sys.path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.config import cfg


def set_nsp_path(path: str) -> None:
    """设置NSP文件路径"""
    cfg.nsp_path.value = path
    cfg.save()
    logger.info(f"NSP路径已设置为: {path}")
    
def start_nsp_exe() -> bool:
    """启动neuroSangSpider.exe
    
    Returns:
        bool: 成功启动返回True，失败返回False
    """
    nsp_path = cfg.nsp_path.value
    if not nsp_path:
        logger.error("NSP路径未设置")
        return False
    
    nsp_file = Path(nsp_path)
    
    # 检查文件是否存在
    if not nsp_file.exists():
        logger.error(f"NSP文件不存在: {nsp_path}")
        return False
    
    # 检查是否为可执行文件
    if not nsp_file.suffix.lower() == '.exe':
        logger.error(f"文件不是可执行文件: {nsp_path}")
        return False
    
    try:
        # 使用win32api.ShellExecute启动，确保完全独立
        logger.info(f"正在启动NSP程序: {nsp_path}")
        
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
                    None,                           # 应用程序名（None表示从命令行获取）
                    f'"{str(nsp_file)}"',          # 命令行（程序路径）
                    None,                           # 进程安全属性
                    None,                           # 线程安全属性
                    False,                          # 不继承句柄
                    creation_flags,                 # 创建标志
                    None,                           # 环境变量（None表示继承）
                    str(nsp_file.parent),          # 工作目录
                    startup_info                    # 启动信息
                )
                
                # 立即关闭进程和线程句柄，完全断开关系
                win32api.CloseHandle(process_info[0])  # 进程句柄
                win32api.CloseHandle(process_info[1])  # 线程句柄
                
                logger.info(f"NSP程序已通过CreateProcess独立启动，PID: {process_info[2]}")
                
            except ImportError:
                logger.error("win32api模块未安装，无法使用CreateProcess")
                logger.info("请安装pywin32: pip install pywin32")
                return False
            except Exception as e:
                logger.error(f"CreateProcess启动失败: {e}")
                return False
        else:
            # 非Windows系统使用nohup
            nohup_path = os.path.join(nsp_file.parent, "nohup.out")
            process = subprocess.Popen(
                f"nohup {str(nsp_file)} > {nohup_path} 2>&1 &",
                cwd=str(nsp_file.parent),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
            logger.info("NSP程序已通过nohup启动, PROCESS: {process}")
        
        return True
        
    except FileNotFoundError:
        logger.error(f"找不到可执行文件: {nsp_path}")
        return False
    except PermissionError:
        logger.error(f"没有权限执行文件: {nsp_path}")
        return False
    except Exception as e:
        logger.error(f"启动NSP程序失败: {e}")
        return False

def start_nsp_exe_blocking() -> tuple[bool, str]:
    """启动neuroSangSpider.exe并等待执行完成
    
    Returns:
        tuple[bool, str]: (是否成功, 输出信息)
    """
    nsp_path = cfg.nsp_path.value
    if not nsp_path:
        return False, "NSP路径未设置"
    
    nsp_file = Path(nsp_path)
    
    if not nsp_file.exists():
        return False, f"NSP文件不存在: {nsp_path}"
    
    try:
        # 方法2: 使用subprocess.run (阻塞，等待完成)
        logger.info(f"正在启动NSP程序: {nsp_path}")
        result = subprocess.run(
            [str(nsp_file)],
            cwd=str(nsp_file.parent),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            logger.info("NSP程序执行成功")
            return True, result.stdout
        else:
            logger.error(f"NSP程序执行失败，返回码: {result.returncode}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error("NSP程序执行超时")
        return False, "程序执行超时"
    except Exception as e:
        logger.error(f"启动NSP程序失败: {e}")
        return False, str(e)

def check_nsp_running() -> bool:
    """检查NSP程序是否正在运行
    
    Returns:
        bool: 正在运行返回True
    """
    try:
        # 在Windows上检查进程
        if os.name == 'nt':
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq NeuroSongSpider.exe'],
                capture_output=True,
                text=True
            )
            return 'NeuroSongSpider.exe' in result.stdout
        else:
            # Linux/Mac
            result = subprocess.run(
                ['pgrep', '-f', 'NeuroSongSpider'],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
    except Exception as e:
        logger.error(f"检查进程失败: {e}")
        return False

def get_nsp_folder_size() -> tuple[bool, str]:
    """获取NSP文件夹占用情况
    
    Returns:
        tuple[bool, str]: (是否成功, 大小信息)
    """
    nsp_path = cfg.nsp_path.value
    if not nsp_path:
        return False, "NSP路径未设置"
    
    nsp_file = Path(nsp_path)
    if not nsp_file.exists():
        return False, f"NSP文件不存在: {nsp_path}"
    
    try:
        nsp_folder = nsp_file.parent
        total_size = 0
        file_count = 0
        
        # 遍历文件夹计算大小
        for file_path in nsp_folder.rglob('*'):
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
        folder_info = f"文件夹: {nsp_folder.name}\n路径: {nsp_folder}\n总大小: {formatted_size}\n文件数量: {file_count}"
        
        logger.info(f"NSP文件夹大小: {formatted_size}, 文件数: {file_count}")
        return True, folder_info
        
    except Exception as e:
        error_msg = f"获取文件夹大小失败: {e}"
        logger.error(error_msg)
        return False, error_msg

def get_nsp_memory_usage() -> tuple[bool, str]:
    """获取NSP进程内存占用情况
    
    Returns:
        tuple[bool, str]: (是否成功, 内存信息)
    """
    try:
        nsp_processes = []
        
        # 查找NSP相关进程
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if 'NeuroSongSpider' in proc.info['name'] or 'neurosongspider' in proc.info['name'].lower():
                    nsp_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not nsp_processes:
            return False, "未找到NSP进程"
        
        memory_info = []
        total_memory = 0
        
        for proc in nsp_processes:
            try:
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024  # 转换为MB
                cpu_percent = proc.cpu_percent()
                total_memory += memory_mb
                
                proc_info = f"PID: {proc.info['pid']}\n"
                proc_info += f"进程名: {proc.info['name']}\n"
                proc_info += f"内存占用: {memory_mb:.2f} MB\n"
                proc_info += f"CPU使用率: {cpu_percent:.1f}%"
                
                memory_info.append(proc_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if memory_info:
            result = f"找到 {len(nsp_processes)} 个NSP进程\n"
            result += f"总内存占用: {total_memory:.2f} MB\n\n"
            result += "\n" + "="*40 + "\n".join(memory_info)
            
            logger.info(f"NSP进程内存占用: {total_memory:.2f} MB")
            return True, result
        else:
            return False, "无法获取进程信息"
            
    except Exception as e:
        error_msg = f"获取内存使用情况失败: {e}"
        logger.error(error_msg)
        return False, error_msg

def get_nsp_version() -> tuple[bool, str]:
    """检查NSP版本号
    
    Returns:
        tuple[bool, str]: (是否成功, 版本信息)
    """
    nsp_path = cfg.nsp_path.value
    if not nsp_path:
        return False, "NSP路径未设置"
    
    nsp_file = Path(nsp_path)
    if not nsp_file.exists():
        return False, f"NSP文件不存在: {nsp_path}"
    
    try:
        # 尝试获取文件版本信息 方法1 (Windows)
        if os.name == 'nt':
            try:
                import win32api
                info = win32api.GetFileVersionInfo(str(nsp_file), "\\")
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{(ms >> 16) & 0xFFFF}.{ms & 0xFFFF}.{(ls >> 16) & 0xFFFF}.{ls & 0xFFFF}"
                
                # 获取更多文件信息
                try:
                    fixed_info = win32api.GetFileVersionInfo(str(nsp_file), "\\StringFileInfo\\040904b0\\")
                    product_name = fixed_info.get('ProductName', 'Unknown')
                    file_description = fixed_info.get('FileDescription', 'Unknown')
                    company_name = fixed_info.get('CompanyName', 'Unknown')
                    
                    version_info = f"文件: {nsp_file.name}\n"
                    version_info += f"版本: {version}\n"
                    version_info += f"产品名称: {product_name}\n"
                    version_info += f"文件描述: {file_description}\n"
                    version_info += f"公司: {company_name}"
                    
                except Exception as e:
                    logger.warning(f"获取Windows文件信息失败: {e}")
                    version_info = f"文件: {nsp_file.name}\n版本: {version}"
                
                logger.info(f"NSP版本: {version}")
                return True, version_info
                
            except ImportError:
                logger.warning("win32api未安装，使用备选方法")
            except Exception as e:
                logger.warning(f"获取Windows版本信息失败: {e}")
        
        # 方法2: 尝试运行程序获取版本信息
        try:
            result = subprocess.run(
                [str(nsp_file), '--version'],
                capture_output=True,
                text=True,
                timeout=3  # 减少超时时间
            )
            if result.returncode == 0 and result.stdout.strip():
                version_info = f"文件: {nsp_file.name}\n版本信息: {result.stdout.strip()}"
                return True, version_info
        except subprocess.TimeoutExpired:
            logger.warning("版本检查超时")
        except Exception:
            pass
        
        # 方法3: 尝试其他版本参数（跳过可能有问题的参数）
        for version_arg in ['-v']:  # 只尝试简单的参数
            try:
                result = subprocess.run(
                    [str(nsp_file), version_arg],
                    capture_output=True,
                    text=True,
                    timeout=2  # 更短的超时时间
                )
                if result.stdout and ('version' in result.stdout.lower() or 'v' in result.stdout.lower()[:10]):
                    version_info = f"文件: {nsp_file.name}\n版本信息: {result.stdout.strip()[:200]}"
                    return True, version_info
            except Exception as e:
                logger.warning(f"[方法三]获取版本信息失败: {e}")
                continue
        
        # 方法4: 返回文件基本信息
        file_stat = nsp_file.stat()
        import time
        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
        file_size = file_stat.st_size / 1024 / 1024  # MB
        
        basic_info = f"文件: {nsp_file.name}\n"
        basic_info += f"大小: {file_size:.2f} MB\n"
        basic_info += f"修改时间: {modified_time}\n"
        basic_info += "说明: 无法获取版本信息，显示文件基本信息"
        
        logger.info("无法获取NSP版本信息，返回文件基本信息")
        return True, basic_info
        
    except Exception as e:
        error_msg = f"检查版本失败: {e}"
        logger.error(error_msg)
        return False, error_msg


if __name__ == "__main__":
    # 测试用例
    test_path = "C:/neuroSangSpider/NeuroSongSpider.exe"
    
    print("=== NSP处理器测试 ===")
    
    # 设置路径
    set_nsp_path(test_path)
    print(f"当前NSP路径: {cfg.nsp_path.value}")
    
    # 检查文件是否存在
    nsp_file = Path(test_path)
    if nsp_file.exists():
        print("✅ NSP文件存在")
        
        print("\n" + "="*50)
        print("📋 版本信息:")
        success, version_info = get_nsp_version()
        if success:
            print(version_info)
        else:
            print(f"❌ {version_info}")
        
        print("\n" + "="*50)
        print("📁 文件夹占用情况:")
        success, folder_info = get_nsp_folder_size()
        if success:
            print(folder_info)
        else:
            print(f"❌ {folder_info}")
        
        print("\n" + "="*50)
        print("🔍 进程状态检查:")
        if check_nsp_running():
            print("⚠️  NSP程序已在运行")
            
            print("\n📊 内存占用情况:")
            success, memory_info = get_nsp_memory_usage()
            if success:
                print(memory_info)
            else:
                print(f"❌ {memory_info}")
        else:
            print("ℹ️  NSP程序未运行")
            
            # 询问是否启动
            print("\n🚀 启动选项:")
            try:
                user_input = input("是否启动NSP程序? (y/N): ").strip().lower()
                if user_input in ['y', 'yes', '是']:
                    if start_nsp_exe():
                        print("✅ NSP程序启动成功")
                        
                        # 启动后再次检查内存
                        import time
                        print("等待3秒后检查内存占用...")
                        time.sleep(3)
                        success, memory_info = get_nsp_memory_usage()
                        if success:
                            print("\n📊 启动后内存占用:")
                            print(memory_info)
                    else:
                        print("❌ NSP程序启动失败")
                else:
                    print("已取消启动")
            except KeyboardInterrupt:
                print("\n\n已中断操作")
    else:
        print("❌ NSP文件不存在，请检查路径")
        print("💡 提示：请确保路径正确，例如:")
        print("   C:/path/to/NeuroSongSpider.exe")
        print("   D:/Games/NeuroSongSpider/NeuroSongSpider.exe")
        
    print("\n" + "="*50)
    
    # 如果NSP已经成功启动，提示用户可以关闭脚本
    if check_nsp_running():
        print("✅ NSP程序已成功启动并正在运行！")
        print("💡 脚本工作已完成，您可以安全地关闭此窗口")
        print("   NSP程序将继续在后台运行")
    
    print("🎯 测试完成！")