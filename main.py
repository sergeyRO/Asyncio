import asyncio
from aiohttp import ClientSession
from database import engine, Base, Session, Pers
import re


async def get_persons(num: int, client: ClientSession):
    url = f"https://swapi.dev/api/people?page={num}"
    async with await client.get(url) as response:
        json_data = await response.json()
        return json_data

async def get_obj(x:str, url: str, client: ClientSession):
    async with await client.get(url) as response:
        json_data = await response.json()
        return json_data[x]

async def paste_to_db(list_peoples):
    async with Session() as session:
        people_list_orm = [Pers(id=item['id'],
                                films=', '.join(item['films']),
                                species=', '.join(item['species']),
                                starships=', '.join(item['starships']),
                                vehicles=', '.join(item['vehicles']))
                           for item in list_peoples]
        session.add_all(people_list_orm)
        await session.commit()

async def main():
    i = 1
    k = 2
    exit_while = 0
    tasks = []
    async with ClientSession() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        while True:
            coro = [get_persons(num=item, client=session) for item in range(i, k)]
            responses = await asyncio.gather(*coro)
            for response in responses:
                if not 'detail' in response.keys():
                    peoples = []
                    for result in response['results']:
                        arr_el = {}
                        arr_el['id'] = int(re.sub("[^0-9]", "", result['url']))
                        arr_el['films'] = result['films']
                        arr_el['species'] = result['species']
                        arr_el['starships'] = result['starships']
                        arr_el['starships'] = result['starships']
                        arr_el['vehicles'] = result['vehicles']
                        peoples.append(arr_el)

                    for people in peoples:
                        if len(people['films']) != 0:
                            coro_films = [get_obj(x='title', url=item, client=session) for item in people['films']]
                            response_films = await asyncio.gather(*coro_films)
                            people['films'] = response_films
                        if len(people['species']) != 0:
                            coro_species = [get_obj(x='name', url=item, client=session) for item in people['species']]
                            response_species = await asyncio.gather(*coro_species)
                            people['species'] = response_species
                        if len(people['starships']) != 0:
                            coro_starships = [get_obj(x='name', url=item, client=session) for item in people['starships']]
                            response_starships = await asyncio.gather(*coro_starships)
                            people['starships'] = response_starships
                        if len(people['vehicles']) != 0:
                            coro_vehicles = [get_obj(x='name', url=item, client=session) for item in people['vehicles']]
                            response_vehicles = await asyncio.gather(*coro_vehicles)
                            people['vehicles'] = response_vehicles
                    db_coro = paste_to_db(peoples)
                    paste_to_db_task = asyncio.create_task(db_coro)
                    tasks.append(paste_to_db_task)
                else:
                    exit_while = 1
            if exit_while == 1:
                break
            i = k
            k += 2
    tasks = asyncio.all_tasks() - {asyncio.current_task()}
    for task in tasks:
        await task

#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

