import os
import shutil

def delete_all_in_current_folder():
    # 현재 디렉토리 경로
    current_folder = os.getcwd()
    
    # 현재 폴더 내의 모든 파일과 디렉토리 목록 가져오기
    for item in os.listdir(current_folder):
        item_path = os.path.join(current_folder, item)
        
        try:
            # 디렉토리라면 삭제
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:  # 파일이라면 삭제
                os.remove(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

    print("All files and directories in the current folder have been deleted.")

# 함수 호출
delete_all_in_current_folder()