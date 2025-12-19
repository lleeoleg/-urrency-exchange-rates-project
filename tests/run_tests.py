import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Запускает все тесты и создает отчет"""
    print("=" * 60)
    print("Запуск тестов проекта 'Курсы валют'")
    print("=" * 60)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",  
        "--tb=short", 
        "--cov=database", 
        "--cov=controller",  
        "--cov-report=term-missing", 
        "--cov-report=html:tests/htmlcov",
        "--junit-xml=tests/test-results.xml"
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        
        print()
        print("=" * 60)
        if result.returncode == 0:
            print("✓ Все тесты прошли успешно!")
        else:
            print(f"✗ Некоторые тесты не прошли (код возврата: {result.returncode})")
        print("=" * 60)
        print()
        print("Отчеты:")
        print("- HTML отчет: tests/htmlcov/index.html")
        print("- XML отчет: tests/test-results.xml")
        
        return result.returncode
    except Exception as e:
        print(f"Ошибка при запуске тестов: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

