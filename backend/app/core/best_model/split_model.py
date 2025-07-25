import os
import argparse
from pathlib import Path

def split_file(file_path, max_chunk_size=50*1024*1024):
    """
    将大文件分割成多个不超过指定大小的块
    
    参数:
        file_path (str): 要分割的文件路径
        max_chunk_size (int): 每个分块的最大大小（字节），默认50MB
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"错误: 文件 {file_path} 不存在")
        return
    
    # 创建输出目录
    output_dir = file_path.parent / f"{file_path.stem}_chunks"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 计算需要的分块数
    file_size = file_path.stat().st_size
    num_chunks = (file_size + max_chunk_size - 1) // max_chunk_size
    
    print(f"文件大小: {file_size / (1024*1024):.2f} MB")
    print(f"分块大小: {max_chunk_size / (1024*1024):.2f} MB")
    print(f"预计分块数: {num_chunks}")
    
    # 读取文件并分割
    with open(file_path, 'rb') as f:
        for i in range(1, num_chunks + 1):
            # 计算当前块的实际大小
            chunk_size = min(max_chunk_size, file_size - (i-1)*max_chunk_size)
            
            # 读取数据块
            chunk = f.read(chunk_size)
            if not chunk:
                break
                
            # 写入分块文件
            chunk_file = output_dir / f"{file_path.name}.part{i:03d}"
            with open(chunk_file, 'wb') as chunk_f:
                chunk_f.write(chunk)
                
            print(f"已创建分片 {i}/{num_chunks}: {chunk_file.name} ({len(chunk) / (1024*1024):.2f} MB)")
    
    print(f"\n分割完成！分片文件保存在: {output_dir}")
    print(f"要合并文件，请运行: python merge_model.py {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='将大文件分割成多个小文件')
    parser.add_argument('file_path', help='要分割的文件路径')
    parser.add_argument('--chunk-size', type=int, default=50*1024*1024,
                       help='每个分块的最大大小（字节），默认50MB')
    
    args = parser.parse_args()
    split_file(args.file_path, args.chunk_size)
