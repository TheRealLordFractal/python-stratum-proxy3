import asyncio
import functools
import logging
import signal
import yaml
import json


async def handle_client(reader, writer, config, connection_limit):
    async with connection_limit:
        try:
            upstream_reader, upstream_writer = await asyncio.open_connection(
                config['upstream_host'], config['upstream_port'])
        except Exception as e:
            logging.error(f"Failed to connect to upstream {config['upstream_host']}:{config['upstream_port']}: {e}")
            writer.close()
            await writer.wait_closed()
            return

        logging.info('Connected to upstream %s:%d', config['upstream_host'],
                     config['upstream_port'])

        async def read_upstream():
            while True:
                data = await upstream_reader.read(8192)
                if not data:
                    break
                for line in data.decode().split('\n'):
                    if line.strip():
                        logging.debug('Received from upstream: %s', line.strip())
                        writer.write(line.encode() + b'\n')
                        await writer.drain()

        read_upstream_task = asyncio.create_task(read_upstream())

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break

                for line in data.decode().split('\n'):
                    if line.strip():
                        json_data = json.loads(line.strip())

                        # Check if the method is 'mining.authorize' and replace the worker's username
                        if json_data.get('method') == 'mining.authorize':
                            json_data['params'][0] = f"{config['workername_modifier']}.{config['workername_override']}"
                            line = json.dumps(json_data)

                        upstream_writer.write((line + '\n').encode())
                        await upstream_writer.drain()

        finally:
            read_upstream_task.cancel()
            await read_upstream_task

            upstream_writer.close()
            await upstream_writer.wait_closed()

async def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Set the logging level from the config file
    log_level = config.get('log_level', 'WARNING').upper()
    if log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        logging.basicConfig(level=getattr(logging, log_level))
    else:
        logging.basicConfig(level=logging.WARNING)
        logging.warning(f"Invalid log level '{log_level}' in config.yml, defaulting to 'WARNING'.")

    connection_limit = asyncio.Semaphore(config.get('max_connections', 100))

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, config, connection_limit),
        config['listen_host'], config['listen_port'])

    logging.info('Listening on %s:%d', config['listen_host'], config['listen_port'])

    stop_event = asyncio.Event()

    def shutdown(signal, event):
        logging.info(f"Received exit signal {signal.name}...")
        event.set()

    signals = (signal.SIGINT, signal.SIGTERM)
    for s in signals:
        asyncio.get_running_loop().add_signal_handler(s, functools.partial(shutdown, s, stop_event))

    async with server:
        await stop_event.wait()
        logging.info("Shutting down server...")
        server.stop()

if __name__ == '__main__':
    asyncio.run(main())
