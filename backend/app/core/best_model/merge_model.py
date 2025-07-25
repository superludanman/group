import os
import argparse
from pathlib import Path

def merge_files(input_dir, output_file=None):
    input_dir = Path(input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"错误: 目录 {input_dir} 不存在或不是目录")
        return
    
    # 获取所有分片文件并按名称排序
    chunk_files = sorted([f for f in input_dir.glob("*.part*")])
    if not chunk_files:
        print(f"错误: 在 {input_dir} 中找不到分片文件")
        return
    
    # 如果没有指定输出文件，则使用原始文件名
    if output_file is None:
        # 从第一个分片文件名中提取原始文件名
        first_chunk = chunk_files[0].name
        # 确保保留原始文件扩展名
        if 'model.safetensors' in first_chunk:
            base_name = 'model.safetensors'
        else:
            base_name = first_chunk.rsplit('.part', 1)[0] + '.safetensors'
        output_file = input_dir.parent / base_name
    else:
        output_file = Path(output_file)
    
    # 合并文件
    with open(output_file, 'wb') as out_f:
        for chunk_file in chunk_files:
            print(f"正在合并: {chunk_file}")
            with open(chunk_file, 'rb') as in_f:
                out_f.write(in_f.read())
    
    print(f"\n合并完成！输出文件: {output_file}")
    print(f"原始大小: {sum(f.stat().st_size for f in chunk_files) / (1024*1024):.2f} MB")
    print(f"合并后大小: {output_file.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='合并分割的文件')
    parser.add_argument('input_dir', help='包含分片文件的目录')
    parser.add_argument('--output', '-o', help='合并后的输出文件路径')
    
    args = parser.parse_args()
    merge_files(args.input_dir, args.output)
