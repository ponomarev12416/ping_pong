import asyncio
import random
import logging
from time import sleep

from multiprocessing import Process


class Server:

    def __init__(self):
        self.response_number = -1
        # Содержит информацию о подключениях
        # Сервер хранит ссылки на все объекты типа StreamWriter
        self.clients = {}
        self.client_count = 0
        asyncio.get_event_loop().create_task(self.start_messaging())


    async def start_messaging(self):
        '''
        Отправляет сообщения клиентам
        '''
        while True:
            disconnected = []
            await asyncio.sleep(5)
            self.response_number += 1
            response_number = self.response_number
            message = f'[{response_number}] KEEPALIVE\0x0A'
            data = message.encode('ascii')
            for port, client in self.clients.items():
                try:
                    client[1].write(data)
                    await client[1].drain()
                except ConnectionResetError:
                    disconnected.append(port)
            for port in disconnected:
                del self.clients[port]


    async def handle_message(self, reader, writer):
        self.client_count += 1
        client_number = self.client_count
        addr = writer.get_extra_info('peername')
        self.clients[addr[1]] = (client_number, writer)
        try:
            while True:
                data = await reader.read(100)
                decoded_data = data.decode('ascii')
                logging.info(decoded_data)
                if random.randint(1, 10) == 10:
                    logging.error('(проигнороировано)')
                    continue
                if not data:
                    break
                request_number = self.__extract_request_number(decoded_data)
                self.response_number += 1
                response_number = self.response_number
                message = f'[{response_number}/{request_number}] PONG'
                addr = writer.get_extra_info('peername')
                logging.info(message)
                writer.write(message.encode('ascii'))
                await writer.drain()
        except Exception as e:
                print(e)
        finally:
                writer.close()
                await writer.wait_closed()


    def __extract_request_number(self, request):
        '''
        Извлекает номер сообщения

        Из полученного тексового сообщения извлекается число,
        находящееся в квадратных скобках.

        Parameters
        ----------
        request: str
            текстовое сообщение

        Returns
        -------
        str
            число в строковом формате
        '''
        start = request.find('[') + 1
        end = request.rfind(']')
        request_number = request[start:end]
        return request_number


async def run():
    main_server = Server()
    server = await asyncio.start_server(
        main_server.handle_message, '127.0.0.1', 8889)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')
    async with server:
        await server.serve_forever()


def main():
    asyncio.run(run())

if __name__ == '__main__':
    logging.basicConfig(
        filename='server.log',
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s.%(msecs)03d;\n%(message)s',
        datefmt='%Y-%m-%d;\n%H:%M:%S',
    )
    logging.basicConfig(
        filename='server.log',
        level=logging.ERROR,
        encoding='utf-8',
    )
    process = Process(target=main)
    process.start()
    sleep(60 * 5)
    process.terminate()
    print('Server is shutdown')
