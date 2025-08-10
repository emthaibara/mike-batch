import os
import sys
import stat

def set_file_only_read(path):
    # 文件写入完成后，立即设置只读权限
    try:
        if sys.platform.startswith('win'):
            # Windows：设置只读属性
            os.chmod(path, stat.S_IREAD)
        else:
            # Linux/macOS：设置只读权限
            os.chmod(path, 0o444)
    except Exception as e:
        print(f"无法设置文件权限：{e}")
