import asyncio
from pathlib import Path

from app.service.meta_service import MetaService


async def init_main():
    file_path = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'
    service = MetaService()
    await service.build(str(file_path))


if __name__ == '__main__':
    asyncio.run(init_main())
