import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass  
class Provider:
    """云服务提供商数据模型"""
    name: str
    display_name: str
    color: str
    api_endpoint: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Country:
    """国家数据模型"""
    country_code: str
    country_name: str
    continent: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class AvailabilityZone:
    """可用区域数据模型"""
    provider_id: int
    region_id: str
    region_name: str
    country_code: str
    continent: str
    status: str = 'available'
    id: Optional[int] = None
    last_updated: Optional[datetime] = None


@dataclass
class UpdateLog:
    """数据更新日志模型"""
    provider_id: int
    status: str
    message: str
    id: Optional[int] = None
    update_time: Optional[datetime] = None


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = 'database/cloud_az.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库连接"""
        pass
    
    def create_tables(self):
        """创建所有数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建云服务提供商表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            color TEXT NOT NULL,
            api_endpoint TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建国家表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT UNIQUE NOT NULL,
            country_name TEXT NOT NULL,
            continent TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建可用区域表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS availability_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER NOT NULL,
            region_id TEXT NOT NULL,
            region_name TEXT NOT NULL,
            country_code TEXT NOT NULL,
            continent TEXT NOT NULL,
            status TEXT DEFAULT 'available',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provider_id) REFERENCES providers(id),
            FOREIGN KEY (country_code) REFERENCES countries(country_code)
        )
        ''')
        
        # 创建数据更新记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS update_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER NOT NULL,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            message TEXT,
            FOREIGN KEY (provider_id) REFERENCES providers(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_provider(self, provider: Provider) -> Optional[int]:
        """创建云服务提供商记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO providers (name, display_name, color, api_endpoint)
            VALUES (?, ?, ?, ?)
            ''', (provider.name, provider.display_name, provider.color, provider.api_endpoint))
            
            provider_id = cursor.lastrowid
            conn.commit()
            return provider_id
        except sqlite3.Error:
            return None
        finally:
            conn.close()
    
    def get_provider(self, provider_id: int) -> Optional[Provider]:
        """根据ID获取云服务提供商"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, display_name, color, api_endpoint, created_at
        FROM providers WHERE id = ?
        ''', (provider_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Provider(
                id=row[0],
                name=row[1],
                display_name=row[2],
                color=row[3],
                api_endpoint=row[4],
                created_at=datetime.fromisoformat(row[5]) if row[5] else None
            )
        return None
    
    def get_provider_by_name(self, name: str) -> Optional[Provider]:
        """根据名称获取云服务提供商"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, display_name, color, api_endpoint, created_at
        FROM providers WHERE name = ?
        ''', (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Provider(
                id=row[0],
                name=row[1],
                display_name=row[2],
                color=row[3],
                api_endpoint=row[4],
                created_at=datetime.fromisoformat(row[5]) if row[5] else None
            )
        return None
    
    def create_country(self, country: Country) -> Optional[int]:
        """创建国家记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO countries (country_code, country_name, continent)
            VALUES (?, ?, ?)
            ''', (country.country_code, country.country_name, country.continent))
            
            country_id = cursor.lastrowid
            conn.commit()
            return country_id
        except sqlite3.Error:
            return None
        finally:
            conn.close()
    
    def get_country(self, country_id: int) -> Optional[Country]:
        """根据ID获取国家"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, country_code, country_name, continent, created_at
        FROM countries WHERE id = ?
        ''', (country_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Country(
                id=row[0],
                country_code=row[1],
                country_name=row[2],
                continent=row[3],
                created_at=datetime.fromisoformat(row[4]) if row[4] else None
            )
        return None
    
    def create_availability_zone(self, az: AvailabilityZone) -> Optional[int]:
        """创建可用区域记录（带去重）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 使用INSERT OR IGNORE避免重复，然后UPDATE
            cursor.execute('''
            INSERT OR IGNORE INTO availability_zones 
            (provider_id, region_id, region_name, country_code, continent, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (az.provider_id, az.region_id, az.region_name, 
                  az.country_code, az.continent, az.status))
            
            # 总是更新记录以确保数据最新
            cursor.execute('''
            UPDATE availability_zones 
            SET region_name = ?, country_code = ?, continent = ?, 
                status = ?, last_updated = CURRENT_TIMESTAMP
            WHERE provider_id = ? AND region_id = ?
            ''', (az.region_name, az.country_code, az.continent, 
                  az.status, az.provider_id, az.region_id))
            
            # 获取记录ID
            cursor.execute('''
            SELECT id FROM availability_zones 
            WHERE provider_id = ? AND region_id = ?
            ''', (az.provider_id, az.region_id))
            
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
                
        except sqlite3.Error as e:
            print(f"Database error in create_availability_zone: {e}")
            return None
        finally:
            conn.close()
    
    def get_availability_zone(self, az_id: int) -> Optional[AvailabilityZone]:
        """根据ID获取可用区域"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, provider_id, region_id, region_name, country_code, 
               continent, status, last_updated
        FROM availability_zones WHERE id = ?
        ''', (az_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return AvailabilityZone(
                id=row[0],
                provider_id=row[1],
                region_id=row[2],
                region_name=row[3],
                country_code=row[4],
                continent=row[5],
                status=row[6],
                last_updated=datetime.fromisoformat(row[7]) if row[7] else None
            )
        return None
    
    def get_countries_by_provider(self, provider_name: str) -> List[str]:
        """获取指定云服务商覆盖的国家列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT DISTINCT az.country_code
        FROM availability_zones az
        JOIN providers p ON az.provider_id = p.id
        WHERE p.name = ? AND az.status = 'available'
        ''', (provider_name,))
        
        countries = [row[0] for row in cursor.fetchall()]
        conn.close()
        return countries
    
    def create_update_log(self, log: UpdateLog) -> Optional[int]:
        """创建更新日志记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO update_logs (provider_id, status, message)
            VALUES (?, ?, ?)
            ''', (log.provider_id, log.status, log.message))
            
            log_id = cursor.lastrowid
            conn.commit()
            return log_id
        except sqlite3.Error:
            return None
        finally:
            conn.close()
    
    def get_update_log(self, log_id: int) -> Optional[UpdateLog]:
        """根据ID获取更新日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, provider_id, update_time, status, message
        FROM update_logs WHERE id = ?
        ''', (log_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UpdateLog(
                id=row[0],
                provider_id=row[1],
                update_time=datetime.fromisoformat(row[2]) if row[2] else None,
                status=row[3],
                message=row[4]
            )
        return None
    
    def get_all_countries_with_providers(self) -> List[Dict[str, Any]]:
        """获取所有国家及其云服务商信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT c.country_code, c.country_name, c.continent,
               GROUP_CONCAT(p.name) as providers
        FROM countries c
        LEFT JOIN availability_zones az ON c.country_code = az.country_code
        LEFT JOIN providers p ON az.provider_id = p.id
        WHERE az.status = 'available' OR az.status IS NULL
        GROUP BY c.country_code, c.country_name, c.continent
        ''')
        
        countries_data = []
        for row in cursor.fetchall():
            providers = row[3].split(',') if row[3] else []
            countries_data.append({
                'country_code': row[0],
                'country_name': row[1],
                'continent': row[2],
                'providers': providers
            })
        
        conn.close()
        return countries_data
