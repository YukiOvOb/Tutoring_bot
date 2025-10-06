from DrissionPage import ChromiumPage
import pandas as pd
import time
import os
import random
import logging
from datetime import datetime
from config import MESSAGE_SETTINGS, DELAY_SETTINGS, EXCEL_SETTINGS, BROWSER_SETTINGS, SAFETY_SETTINGS

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'tiktok_messenger_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TikTokMessengerAdvanced:
    def __init__(self):
        """
        初始化高级TikTok消息发送器
        """
        self.page = None
        self.success_count = 0
        self.fail_count = 0
        self.retry_count = 0
        self.current_message = MESSAGE_SETTINGS["message_text"]
        
    def init_browser(self):
        """
        初始化浏览器
        """
        try:
            # 配置浏览器选项
            options = {}
            if BROWSER_SETTINGS.get("user_data_dir"):
                options["user_data_dir"] = BROWSER_SETTINGS["user_data_dir"]
            
            self.page = ChromiumPage(**options)
            
            # 设置窗口大小
            if BROWSER_SETTINGS.get("window_size"):
                width, height = BROWSER_SETTINGS["window_size"]
                self.page.set.window.size(width, height)
                
            logging.info("浏览器初始化成功")
            return True
        except Exception as e:
            logging.error(f"浏览器初始化失败: {e}")
            return False
    
    def load_customer_data(self):
        """
        从Excel文件中加载客户数据
        """
        file_path = EXCEL_SETTINGS["file_path"]
        try:
            df = pd.read_excel(file_path)
            logging.info(f"成功加载 {len(df)} 条客户数据")
            
            # 限制处理数量
            max_users = SAFETY_SETTINGS["max_users_per_run"]
            if len(df) > max_users:
                df = df.head(max_users)
                logging.warning(f"限制处理数量为 {max_users} 条")
                
            return df
        except Exception as e:
            logging.error(f"加载Excel文件失败: {e}")
            return None
    
    def wait_random_time(self, delay_type="random_delay"):
        """
        随机等待时间，避免被检测为机器人
        """
        min_time, max_time = DELAY_SETTINGS.get(delay_type, (1, 3))
        wait_time = random.uniform(min_time, max_time)
        logging.debug(f"等待 {wait_time:.1f} 秒...")
        time.sleep(wait_time)
    
    def get_random_message(self):
        """
        获取随机消息内容
        """
        if SAFETY_SETTINGS["use_random_messages"]:
            messages = MESSAGE_SETTINGS.get("backup_messages", [MESSAGE_SETTINGS["message_text"]])
            return random.choice(messages)
        return MESSAGE_SETTINGS["message_text"]
    
    def click_message_button(self):
        """
        点击消息按钮
        """
        try:
            # 多种可能的消息按钮选择器
            selectors = [
                'css:[data-e2e="message-button"]',
                'css:button:contains("消息")',
                'css:button:contains("Message")',
                'css:.message-button'
            ]
            
            for selector in selectors:
                try:
                    message_button = self.page.ele(selector, timeout=5)
                    if message_button and message_button.states.is_enabled:
                        message_button.click()
                        logging.info("成功点击消息按钮")
                        self.wait_random_time("click_delay")
                        return True
                except:
                    continue
            
            logging.warning("未找到可用的消息按钮")
            return False
            
        except Exception as e:
            logging.error(f"点击消息按钮失败: {e}")
            return False
    
    def send_message(self):
        """
        发送消息
        """
        try:
            # 等待消息输入框加载
            self.wait_random_time("page_load_delay")
            
            # 多种可能的输入框选择器
            input_selectors = [
                'css:[data-e2e="message-input-area"] .public-DraftEditor-content[contenteditable="true"]',
                'css:.public-DraftEditor-content[contenteditable="true"]',
                'css:[contenteditable="true"][role="textbox"]',
                'css:textarea[placeholder*="消息"]',
                'css:textarea[placeholder*="message"]'
            ]
            
            editor = None
            for selector in input_selectors:
                try:
                    editor = self.page.ele(selector, timeout=3)
                    if editor:
                        break
                except:
                    continue
            
            if not editor:
                logging.error("未找到消息编辑器")
                return False
            
            # 点击输入框激活
            editor.click()
            self.wait_random_time("input_delay")
            
            # 获取要发送的消息
            message = self.get_random_message()
            
            # 清空输入框并输入消息
            editor.clear()
            self.wait_random_time("input_delay")
            editor.input(message, clear=False)
            logging.info(f"已输入消息: {message}")
            
            self.wait_random_time("input_delay")
            
            # 尝试发送消息
            # 方法1: 按回车键
            try:
                editor.input('\n')
                logging.info("通过回车键发送消息")
                self.wait_random_time("click_delay")
                return True
            except:
                pass
            
            # 方法2: 查找发送按钮
            send_selectors = [
                'css:[data-e2e="send-button"]',
                'css:button[type="submit"]',
                'css:.send-button',
                'css:button:contains("发送")',
                'css:button:contains("Send")'
            ]
            
            for selector in send_selectors:
                try:
                    send_button = self.page.ele(selector, timeout=2)
                    if send_button and send_button.states.is_enabled:
                        send_button.click()
                        logging.info("通过发送按钮发送消息")
                        self.wait_random_time("click_delay")
                        return True
                except:
                    continue
            
            logging.error("无法发送消息")
            return False
            
        except Exception as e:
            logging.error(f"发送消息失败: {e}")
            return False
    
    def visit_profile_and_send_message(self, profile_url, user_name=""):
        """
        访问用户个人页面并发送消息
        """
        try:
            logging.info(f"正在访问 {user_name}: {profile_url}")
            self.page.get(profile_url)
            
            # 等待页面加载
            self.wait_random_time("page_load_delay")
            
            # 检查页面是否加载成功
            if "tiktok.com" not in self.page.url.lower():
                logging.error(f"页面加载失败或重定向: {self.page.url}")
                return False
            
            # 点击消息按钮
            if self.click_message_button():
                # 发送消息
                if self.send_message():
                    logging.info(f"✅ 消息发送成功: {user_name}")
                    self.success_count += 1
                    return True
                else:
                    logging.error(f"❌ 消息发送失败: {user_name}")
                    self.fail_count += 1
                    return False
            else:
                logging.error(f"❌ 无法点击消息按钮: {user_name}")
                self.fail_count += 1
                return False
                
        except Exception as e:
            logging.error(f"访问个人页面失败 {user_name}: {e}")
            self.fail_count += 1
            return False
    
    def process_all_customers(self):
        """
        处理所有客户数据
        """
        # 初始化浏览器
        if not self.init_browser():
            return False
        
        # 加载客户数据
        df = self.load_customer_data()
        if df is None:
            return False
        
        logging.info(f"开始处理 {len(df)} 个客户...")
        
        columns = EXCEL_SETTINGS["columns"]
        consecutive_failures = 0
        
        for index, row in df.iterrows():
            try:
                # 获取用户信息
                profile_url = row.get(columns["profile_url"], '')
                customer_name = row.get(columns["name"], f'客户{index+1}')
                
                if not profile_url or not str(profile_url).startswith('http'):
                    logging.warning(f"跳过 {customer_name}: 无效的URL")
                    continue
                
                logging.info(f"\n处理第 {index+1}/{len(df)} 个客户: {customer_name}")
                
                # 访问个人页面并发送消息
                success = self.visit_profile_and_send_message(profile_url, customer_name)
                
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                
                # 检查连续失败次数
                if consecutive_failures >= 5:
                    logging.warning(f"连续失败 {consecutive_failures} 次，暂停 {SAFETY_SETTINGS['failure_pause']} 秒")
                    time.sleep(SAFETY_SETTINGS["failure_pause"])
                    consecutive_failures = 0
                
                # 随机等待，避免被限制
                if index < len(df) - 1:  # 不是最后一个
                    self.wait_random_time("next_user_delay")
                    
            except KeyboardInterrupt:
                logging.info("用户中断执行")
                break
            except Exception as e:
                logging.error(f"处理客户 {customer_name} 时出错: {e}")
                self.fail_count += 1
                continue
        
        # 输出统计结果
        total = self.success_count + self.fail_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        logging.info(f"\n=== 处理完成 ===")
        logging.info(f"成功: {self.success_count} 个")
        logging.info(f"失败: {self.fail_count} 个")
        logging.info(f"总计: {total} 个")
        logging.info(f"成功率: {success_rate:.1f}%")
        
        return True
    
    def close(self):
        """
        关闭浏览器
        """
        if self.page:
            try:
                self.page.quit()
                logging.info("浏览器已关闭")
            except:
                pass

def main():
    """
    主函数
    """
    # 检查Excel文件是否存在
    excel_file_path = EXCEL_SETTINGS["file_path"]
    if not os.path.exists(excel_file_path):
        print(f"错误: 找不到文件 {excel_file_path}")
        print("请确保Excel文件在正确的路径下")
        return
    
    # 创建TikTok消息发送器实例
    messenger = TikTokMessengerAdvanced()
    
    try:
        print("=== TikTok 自动消息发送器 (高级版) ===")
        print("请确保:")
        print("1. 已经在浏览器中登录TikTok账号")
        print("2. Excel文件包含正确的用户链接")
        print("3. 网络连接正常")
        print("4. 检查config.py中的配置设置")
        print(f"5. 本次最多处理 {SAFETY_SETTINGS['max_users_per_run']} 个用户")
        
        response = input("\n是否开始执行? (y/n): ")
        if response.lower() != 'y':
            print("取消执行")
            return
        
        # 处理所有客户
        messenger.process_all_customers()
        
    except KeyboardInterrupt:
        logging.info("用户中断执行")
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
    finally:
        # 关闭浏览器
        messenger.close()

if __name__ == "__main__":
    main()