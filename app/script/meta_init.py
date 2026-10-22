import asyncio
from pathlib import Path


from app.service.meta_service import MetaService


async def init_main():
    path = Path(__file__).parent[2] /'conf'/ 'meta_config.py'
    service = MetaService()
    await  service.build(path)

if __name__ == '__main__':
    asyncio.run(init_main())