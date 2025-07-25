import json
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import engine
from backend.app.core.models import Tag

Session = sessionmaker(bind=engine)
session = Session()

with open('Doc_Module/contents1.json', 'r', encoding='utf-8') as f:
    contents = json.load(f)

for tag_name, levels in contents.items():
    for level, description in levels.items():
        # 检查是否已存在，避免重复
        exists = session.query(Tag).filter_by(tag_name=tag_name, level=level).first()
        if exists:
            continue
        tag = Tag(tag_name=tag_name, level=level, description=description)
        session.add(tag)

session.commit()
session.close()
print("导入完成！") 