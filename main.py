from apify import Actor
import asyncio
import subprocess
import json
import os

async def main():
    async with Actor:
        # Récupérer l'input
        actor_input = await Actor.get_input() or {}
        username = actor_input.get('username')
        timeout = actor_input.get('timeout', 30)
        tags = actor_input.get('tags', '')
        
        if not username:
            raise ValueError('Username is required')
        
        Actor.log.info(f'Starting Maigret search for username: {username}')
        
        # Construire la commande Maigret
        cmd = ['maigret', username, '--timeout', str(timeout), '--json', 'ndjson']
        
        if tags:
            cmd.extend(['--tags', tags])
        
        # Exécuter Maigret
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1h max
            )
            
            # Parser les résultats
            output_lines = result.stdout.strip().split('\n')
            
            for line in output_lines:
                if line.strip():
                    try:
                        data = json.loads(line)
                        # Pousser vers le dataset Apify
                        await Actor.push_data({
                            'username': username,
                            'site_name': data.get('site_name'),
                            'url': data.get('url'),
                            'status': data.get('status'),
                            'http_status': data.get('http_status'),
                            'response_time': data.get('response_time')
                        })
                    except json.JSONDecodeError:
                        continue
            
            Actor.log.info(f'Search completed for {username}')
            
        except subprocess.TimeoutExpired:
            Actor.log.error('Maigret execution timed out')
        except Exception as e:
            Actor.log.error(f'Error running Maigret: {str(e)}')
            raise

if __name__ == '__main__':
    asyncio.run(main())
