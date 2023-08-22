import asyncio
import random
import logging


class Client:

    async def start_messaging(self):
        '''
        Отправляет сообщения на сервер.
        '''
        request_number = -1
        while True:
            await asyncio.sleep(random.randint(300, 3000) / 1000)
            request_number += 1
            message = f'[{request_number}] PING\0x0A'
            logging.info(message)
            self.writer.write(message.encode('ascii'))
            await self.writer.drain()


    async def tcp_client(self):
        '''
        Ожидает сообщения от сервера. 
        ''' 
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8889)
        self.writer = writer
        asyncio.get_event_loop().create_task(self.start_messaging())
        while True:
            data = await reader.read(100)
            # Если получено пустое сообщение закрываем соединениео
            if not data:
                break
            message = data.decode('utf-8')
            text = self.__extract_message_text(message)
            if text.find('KEEPALIVE') == -1:
                logging.info(message)
            else:
                logging.warning(message)


    def __extract_message_text(self, message):
        '''
        Извлекает текст сообщения

        Из тексового сообщения извлекаются символы,
        находящиеся правее квадратных скобок.

        Parameters
        ----------
        request: str
            текстовое сообщение

        Returns
        -------
        str
           текст сообщения, без его номера 
        '''
        return message[message.find(']'):].strip()


if __name__ == '__main__':
    logging.basicConfig(
        filename=f'client-{random.randint(0, 100000)}.log',
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s.%(msecs)03d;\n%(message)s',
        datefmt='%Y-%m-%d;\n%H:%M:%S',
    )
    logging.basicConfig(
        filename='client.log',
        level=logging.WARNING,
        encoding='utf-8',
    )
    client = Client()
    asyncio.run(client.tcp_client())
