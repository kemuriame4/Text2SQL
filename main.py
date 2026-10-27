import asyncio
from personal.service.meta_service import MetaService


async def async_main():
    file_path = "personal/config/meta_config.yaml"
    service = MetaService()
    await service.build(file_path)


if __name__ == "__main__":
    asyncio.run(async_main())
