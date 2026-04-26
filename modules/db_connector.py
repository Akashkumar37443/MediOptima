"""
Database Connector Module
Connects to MySQL/PostgreSQL to fetch real hospital data
"""
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnector:
    """Connect to hospital database and fetch real-time data."""
    
    def __init__(self, db_type='mysql', host=None, port=None, 
                 database=None, user=None, password=None):
        """
        Initialize database connection.
        
        Parameters:
        -----------
        db_type : str
            'mysql' or 'postgresql'
        host : str
            Database host (default: localhost)
        port : int
            Database port (default: 3306 for MySQL, 5432 for PostgreSQL)
        database : str
            Database name
        user : str
            Database user
        password : str
            Database password
        """
        self.db_type = db_type.lower()
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 3306 if self.db_type == 'mysql' else 5432))
        self.database = database or os.getenv('DB_NAME', 'hospital_db')
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.connection = None
        
    def connect(self):
        """Establish database connection."""
        try:
            if self.db_type == 'mysql':
                import pymysql
                self.connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    charset='utf8mb4'
                )
                print(f"✅ Connected to MySQL database: {self.database}")
                
            elif self.db_type == 'postgresql':
                import psycopg2
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                print(f"✅ Connected to PostgreSQL database: {self.database}")
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
            return self.connection
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")
    
    def fetch_patient_data(self, days=90):
        """
        Fetch patient admission data from database.
        
        Expected table structure:
        - patient_admissions (date, patient_count, emergency_cases, icu_admissions, 
                             discharge_count, ward_type)
        """
        query = f"""
        SELECT 
            DATE(admission_date) as Date,
            COUNT(*) as Daily_Patients,
            SUM(CASE WHEN is_emergency = 1 THEN 1 ELSE 0 END) as Emergency_Cases,
            SUM(CASE WHEN ward_type = 'ICU' THEN 1 ELSE 0 END) as ICU_Admissions,
            SUM(CASE WHEN discharge_date IS NOT NULL THEN 1 ELSE 0 END) as Discharge_Count
        FROM patient_admissions
        WHERE admission_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY DATE(admission_date)
        ORDER BY Date
        """
        
        return pd.read_sql(query, self.connection)
    
    def fetch_bed_data(self, days=90):
        """
        Fetch bed occupancy data from database.
        
        Expected table structure:
        - bed_inventory (date, bed_type, total_beds, occupied_beds, available_beds)
        """
        query = f"""
        SELECT 
            DATE(date) as Date,
            bed_type,
            total_beds as Total_Beds,
            occupied_beds as Occupied,
            available_beds as Available
        FROM bed_inventory
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        ORDER BY Date
        """
        
        return pd.read_sql(query, self.connection)
    
    def fetch_staff_data(self, days=90):
        """
        Fetch staff scheduling data from database.
        
        Expected table structure:
        - staff_roster (date, role, staff_count, shift)
        """
        query = f"""
        SELECT 
            DATE(date) as Date,
            SUM(CASE WHEN role = 'Doctor' THEN staff_count ELSE 0 END) as Doctors,
            SUM(CASE WHEN role = 'Nurse' THEN staff_count ELSE 0 END) as Nurses,
            SUM(CASE WHEN role = 'ICU Nurse' THEN staff_count ELSE 0 END) as ICU_Nurses
        FROM staff_roster
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY DATE(date)
        ORDER BY Date
        """
        
        return pd.read_sql(query, self.connection)
    
    def get_all_hospital_data(self, days=90):
        """
        Fetch complete hospital dataset combining all tables.
        Returns DataFrame matching the format expected by the app.
        """
        # Fetch patient data
        patient_df = self.fetch_patient_data(days)
        
        # Fetch bed data and pivot
        bed_df = self.fetch_bed_data(days)
        if not bed_df.empty:
            bed_pivot = bed_df.pivot(index='Date', columns='bed_type', values=['Total_Beds', 'Available'])
            bed_pivot.columns = ['General_Total', 'ICU_Total', 'General_Available', 'ICU_Available']
            bed_pivot = bed_pivot.reset_index()
        else:
            bed_pivot = pd.DataFrame()
        
        # Fetch staff data
        staff_df = self.fetch_staff_data(days)
        
        # Combine all data
        combined = patient_df.merge(bed_pivot, on='Date', how='outer')
        combined = combined.merge(staff_df, on='Date', how='outer')
        
        # Add derived fields
        combined['Available_Beds'] = combined.get('General_Available', 0)
        combined['Available_ICU_Beds'] = combined.get('ICU_Available', 0)
        combined['Total_Beds'] = combined.get('General_Total', 350)
        combined['Total_ICU_Beds'] = combined.get('ICU_Total', 45)
        combined['Doctors_On_Duty'] = combined.get('Doctors', 25)
        combined['Nurses_On_Duty'] = combined.get('Nurses', 80)
        combined['ICU_Nurses'] = combined.get('ICU_Nurses', 18)
        
        # Fill missing values
        combined = combined.fillna(method='ffill').fillna(method='bfill')
        
        return combined
    
    def test_connection(self):
        """Test if database connection works."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.disconnect()
            return result is not None
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


def create_mock_db_config():
    """Create example .env file for database configuration."""
    env_content = """# MediOptima Database Configuration
# Copy this to .env and fill in your actual database credentials

# Database Type: mysql or postgresql
DB_TYPE=mysql

# Database Connection
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hospital_db
DB_USER=root
DB_PASSWORD=your_password_here

# Alternative: PostgreSQL
# DB_TYPE=postgresql
# DB_PORT=5432
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("📄 Created .env.example file. Copy to .env and configure your database.")


# Fallback: Mock database connector for testing
class MockDatabaseConnector:
    """Mock connector that returns synthetic data for testing without DB."""
    
    def __init__(self):
        self.data = None
    
    def connect(self):
        print("📊 Using Mock Database (no real connection)")
        return True
    
    def get_all_hospital_data(self, days=90):
        """Generate realistic synthetic data."""
        from data_generator import generate_hospital_data
        return generate_hospital_data(days=days)
    
    def disconnect(self):
        pass


if __name__ == '__main__':
    # Test the database connector
    print("Testing Database Connector...")
    
    # Create example env file
    create_mock_db_config()
    
    # Try to connect using environment variables
    try:
        db = DatabaseConnector()
        if db.test_connection():
            print("✅ Database connection successful!")
            data = db.get_all_hospital_data(days=30)
            print(f"📊 Fetched {len(data)} records")
            print(data.head())
        else:
            print("⚠️ Using mock data (no database connection)")
    except Exception as e:
        print(f"⚠️ Using mock data: {e}")
