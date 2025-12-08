from .quantum_bit_spider import QuantumBitSpider
from .thirty_six_kr_spider import ThirtySixKrSpider
from .pai_com_spider import PaiComSpider
import logging
import threading
import time

logger = logging.getLogger(__name__)

class SpiderManager:
    """爬虫管理器，用于统一管理和调度各个平台的爬虫"""
    
    def __init__(self):
        self.spiders = [
            QuantumBitSpider(),
            ThirtySixKrSpider(),
            PaiComSpider()
        ]
        self.is_running = False
        self.lock = threading.Lock()
    
    def run_all_spiders(self):
        """运行所有爬虫"""
        logger.info("开始运行所有爬虫")
        
        threads = []
        for spider in self.spiders:
            thread = threading.Thread(target=self._run_spider, args=(spider,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        logger.info("所有爬虫运行完成")
    
    def _run_spider(self, spider):
        """运行单个爬虫"""
        try:
            logger.info(f"开始运行 {spider.platform_name} 爬虫")
            spider.crawl_news_list()
            logger.info(f"{spider.platform_name} 爬虫运行完成")
        except Exception as e:
            logger.error(f"{spider.platform_name} 爬虫运行失败: {e}")
        finally:
            spider.close()
    
    def start_scheduled_crawl(self, interval=3600):
        """启动定时爬取
        
        Args:
            interval: 爬取间隔时间（秒），默认3600秒（1小时）
        """
        self.is_running = True
        logger.info(f"启动定时爬取，间隔时间: {interval} 秒")
        
        while self.is_running:
            self.run_all_spiders()
            
            # 等待指定时间
            for _ in range(interval):
                if not self.is_running:
                    break
                time.sleep(1)
    
    def stop_scheduled_crawl(self):
        """停止定时爬取"""
        logger.info("停止定时爬取")
        self.is_running = False
    
    def close(self):
        """关闭所有爬虫资源"""
        self.stop_scheduled_crawl()
        logger.info("关闭所有爬虫资源")
