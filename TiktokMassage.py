from DrissionPage import ChromiumPage
from pathlib import Path
import pandas as pd
from openpyxl import Workbook  
import time
import os
import random

class TikTokMessenger:
    def __init__(self, excel_file_path):
        """
        初始化TikTok消息发送器
        :param excel_file_path: 包含客户信息的Excel文件路径
        """
        self.page = ChromiumPage()
        self.excel_file_path = str(Path(excel_file_path).expanduser().resolve())
        self.message_text = "🌟 Join our Chinese Learning Community on Telegram!\nGet free practice worksheets, PSLE tips, and learning resources prepared by experienced tutors.\n🔗 https://t.me/Learning_Chinese_Tutor"

    def load_customer_data(self):
        """
        从Excel文件中加载客户数据
        """
        try:
            excel_path = Path(self.excel_file_path)
            if not excel_path.exists():
                print(f"加载Excel文件失败: 找不到文件 {excel_path}")
                return None
            df = pd.read_excel(excel_path)
            print(f"成功加载 {len(df)} 条客户数据（文件：{excel_path}）")
            return df
        except Exception as e:
            print(f"加载Excel文件失败: {e}")
            return None
    
    def wait_random_time(self, min_seconds=2, max_seconds=5):
        """
        随机等待时间，避免被检测为机器人
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        print(f"等待 {wait_time:.1f} 秒...")
        time.sleep(wait_time)
    
    def get_row_range(self, total_rows):
        """
        获取用户输入的行范围
        :param total_rows: 总行数
        :return: (start_row, end_row) 或 (None, None) 如果取消
        """
        print(f"\n📊 数据范围选择")
        print(f"Excel文件共有 {total_rows} 行数据")
        print("您可以选择处理的行范围进行测试")
        
        # 显示一些示例
        print(f"\n💡 示例:")
        print(f"  处理第1行: 输入 1 1")
        print(f"  处理前3行: 输入 1 3") 
        print(f"  处理第5-10行: 输入 5 10")
        print(f"  处理所有数据: 输入 1 {total_rows}")
        
        while True:
            try:
                choice = input(f"\n请输入行范围 (格式: 开始行号 结束行号，或输入 'all' 处理全部，'q' 退出): ").strip()
                
                if choice.lower() == 'q':
                    return None, None
                
                if choice.lower() == 'all':
                    return 1, total_rows
                
                # 解析输入
                parts = choice.split()
                if len(parts) == 1:
                    # 只输入一个数字，表示处理单行
                    start_row = end_row = int(parts[0])
                elif len(parts) == 2:
                    # 输入两个数字
                    start_row = int(parts[0])
                    end_row = int(parts[1])
                else:
                    print("❌ 格式错误，请输入1-2个数字")
                    continue
                
                # 验证范围
                if start_row < 1 or end_row < 1:
                    print("❌ 行号必须大于0")
                    continue
                
                if start_row > total_rows or end_row > total_rows:
                    print(f"❌ 行号不能超过总行数 {total_rows}")
                    continue
                
                if start_row > end_row:
                    print("❌ 开始行号不能大于结束行号")
                    continue
                
                # 确认选择             
                if start_row == end_row:
                    print(f"\n✅ 将处理第 {start_row} 行 (共1个客户)")
                else:
                    print(f"\n✅ 将处理第 {start_row}-{end_row} 行 (共{end_row-start_row+1}个客户)")
                
                confirm = input("确认执行? (y/n，回车默认是 y): ").strip().lower()
                # 允许回车直接确认（空字符串）、常见的肯定输入
                if confirm == '' or confirm in ['y', 'yes', '是', '确认']:
                    return start_row, end_row
                elif confirm in ['n', 'no', '否', '取消']:
                    continue
                else:
                    print("请输入 y 或 n（或直接回车确认）")
                    continue    
                    
            except ValueError:
                print("❌ 请输入有效的数字")
                continue
            except KeyboardInterrupt:
                print("\n用户取消操作")
                return None, None
    
    def click_message_button(self):
        """
        点击消息按钮
        """
        try:
            # 查找并点击消息按钮
            message_button = self.page.ele('css:[data-e2e="message-button"]', timeout=10)
            if message_button:
                message_button.click()
                print("成功点击消息按钮")
                self.wait_random_time(3, 6)
                return True
            else:
                print("未找到消息按钮")
                return False
        except Exception as e:
            print(f"点击消息按钮失败: {e}")
            return False
    
    def send_message(self):
        """
        发送消息
        """
        try:
            # 等待消息输入框加载
            self.wait_random_time(2, 4)
            
            # 查找消息输入区域
            input_area = self.page.ele('css:[data-e2e="message-input-area"]', timeout=10)
            if not input_area:
                print("未找到消息输入区域")
                return False
            
            # 查找可编辑的输入框
            editor = self.page.ele('css:.public-DraftEditor-content[contenteditable="true"]', timeout=10)
            if not editor:
                print("未找到消息编辑器")
                return False
            
            # 点击输入框激活
            editor.click()
            self.wait_random_time(1, 2)
            
            # 清空输入框并输入消息
            editor.clear()
            editor.input(self.message_text)
            print(f"已输入消息: {self.message_text}")
            
            self.wait_random_time(1, 3)
            
            # 查找并点击发送按钮 (通常是回车键或发送图标)
            # 尝试按回车键发送
            editor.input('\n')
            print("已发送消息")
            
            self.wait_random_time(3, 6)
            return True
            
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def visit_profile_and_send_message(self, profile_url):
        """
        访问用户个人页面并发送消息
        """
        try:
            print(f"正在访问: {profile_url}")
            self.page.get(profile_url)
            
            # 等待页面加载
            self.wait_random_time(3, 6)
            
            # 点击消息按钮
            if self.click_message_button():
                # 发送消息
                if self.send_message():
                    print("消息发送成功!")
                    return True
                else:
                    print("消息发送失败")
                    return False
            else:
                print("无法点击消息按钮")
                return False
                
        except Exception as e:
            print(f"访问个人页面失败: {e}")
            return False
    
    def process_customers_in_range(self, start_row=None, end_row=None):
        """
        处理指定范围的客户数据
        :param start_row: 开始行号（从1开始，包含该行）
        :param end_row: 结束行号（包含该行）
        """
        # 加载客户数据
        df = self.load_customer_data()
        if df is None:
            return

        total_rows = len(df)
        print(f"Excel文件共有 {total_rows} 行数据")

        # 获取用户输入的行范围
        if start_row is None or end_row is None:
            start_row, end_row = self.get_row_range(total_rows)
        
        if start_row is None or end_row is None:
            print("取消执行")
            return

        # 验证行号范围
        if start_row < 1 or end_row < 1 or start_row > total_rows or end_row > total_rows:
            print(f"错误: 行号范围无效。有效范围是 1-{total_rows}")
            return
        
        if start_row > end_row:
            print("错误: 开始行号不能大于结束行号")
            return

        # 截取指定范围的数据（注意：DataFrame索引从0开始）
        df_selected = df.iloc[start_row-1:end_row]
        
        success_count = 0
        fail_count = 0

        print(f"\n开始处理第 {start_row}-{end_row} 行，共 {len(df_selected)} 个客户...")

        for df_index, (index, row) in enumerate(df_selected.iterrows()):
            try:
                # 根据您的Excel格式读取数据（按列位置）
                # 支持中文列名或字母列名
                sequence_no = row.iloc[0] if len(row) > 0 else index+1  # A列：序号
                nickname = row.iloc[1] if len(row) > 1 else ''  # B列：昵称
                username = row.iloc[2] if len(row) > 2 else ''  # C列：用户名
                profile_url = row.iloc[3] if len(row) > 3 else ''  # D列：用户链接
                crawl_time = row.iloc[4] if len(row) > 4 else ''  # E列：爬取时间
                
                # 使用昵称作为显示名称，如果没有则使用用户名
                customer_name = str(nickname).strip() if nickname else (str(username).strip() if username else f'用户{sequence_no}')
                username_str = str(username).strip() if username else ''
                
                if not profile_url or not str(profile_url).startswith('http'):
                    print(f"跳过 {customer_name}: 没有有效的URL ({profile_url})")
                    continue
                
                actual_row_num = index + 1  # Excel中的实际行号
                progress = f"{df_index+1}/{len(df_selected)}"
                print(f"\n处理第 {progress} 个客户 (Excel第{actual_row_num}行): {customer_name} (@{username_str})")
                print(f"链接: {profile_url}")
                
                # 访问个人页面并发送消息
                if self.visit_profile_and_send_message(profile_url):
                    success_count += 1
                    print(f"✅ 成功发送给 {customer_name} (@{username_str})")
                else:
                    fail_count += 1
                    print(f"❌ 发送失败: {customer_name} (@{username_str})")
                
                # 随机等待，避免被限制
                if df_index < len(df_selected) - 1:  # 不是最后一个
                    self.wait_random_time(10, 20)
                    
            except Exception as e:
                fail_count += 1
                try:
                    customer_name = row.iloc[1] if len(row) > 1 else f'用户{index+1}'
                except:
                    customer_name = f'用户{index+1}'
                print(f"处理客户 {customer_name} 时出错: {e}")
                continue
        
        print(f"\n=== 处理完成 ===")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"总计: {len(df_selected)} 个")
    
    def process_all_customers(self):
        """
        处理所有客户数据（兼容方法）
        """
        df = self.load_customer_data()
        if df is None:
            return
        total_rows = len(df)
        return self.process_customers_in_range(1, total_rows)
    
    def close(self):
        """
        关闭浏览器
        """
        self.page.quit()
        print("浏览器已关闭")

# 使用示例
def main():
    # 改为相对于脚本所在目录查找 tiktok.xlsx
    base_dir = Path(__file__).resolve().parent
    excel_file_path = base_dir / "tiktok.xlsx"  # 如需自定义，改为绝对路径或传入命令行参数

    # 检查文件是否存在
    if not excel_file_path.exists():
        print(f"错误: 找不到文件 {excel_file_path}")
        print("请将 tiktok.xlsx 放到脚本同目录，或将 excel_file_path 改为你的实际绝对路径。")
        print("Excel文件应包含以下列：")
        print("A列：序号, B列：昵称, C列：用户名, D列：用户链接, E列：爬取时间")
        return
    
    # 创建TikTok消息发送器实例
    messenger = TikTokMessenger(str(excel_file_path))
    
    try:
        print("=== TikTok 自动消息发送器 ===")
        print("请确保:")
        print("1. 已经在Chrome浏览器中登录TikTok账号")
        print("2. Excel文件包含正确的用户链接")
        print("3. 网络连接正常")
        print("\nExcel文件格式要求：")
        print("A列：序号, B列：昵称, C列：用户名, D列：用户链接, E列：爬取时间")
        
        # 处理指定范围的客户
        messenger.process_customers_in_range()
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        # 关闭浏览器
        messenger.close()

if __name__ == "__main__":
    main()