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
        
        # Construire la commande Maigret avec sortie JSON
        cmd = ['maigret', username, '--timeout', str(timeout), '--json', 'simple']
        
        if tags:
            cmd.extend(['--tags', tags])
        
        # Log de la commande
        Actor.log.info(f'Running command: {" ".join(cmd)}')
        
        # Exécuter Maigret
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            Actor.log.info(f'Maigret stdout length: {len(result.stdout)}')
            Actor.log.info(f'Maigret stderr: {result.stderr[:500]}')  # Premiers 500 caractères
            
            # Si pas de JSON, essayer de parser la sortie standard
            if result.stdout.strip():
                try:
                    # Essayer de parser comme JSON
                    data = json.loads(result.stdout)
                    
                    # Parcourir les résultats
                    for site_name, site_data in data.items():
                        if isinstance(site_data, dict) and site_data.get('status'):
                            await Actor.push_data({
                                'username': username,
                                'site_name': site_name,
                                'url': site_data.get('url_user', ''),
                                'status': site_data.get('status', {}).get('status'),
                                'http_status': site_data.get('status', {}).get('http_status'),
                                'response_time': site_data.get('status', {}).get('query_time')
                            })
                    
                    Actor.log.info(f'Pushed data for {len(data)} sites')
                    
                except json.JSONDecodeError as e:
                    Actor.log.warning(f'Could not parse JSON: {e}')
                    Actor.log.info(f'Raw output (first 1000 chars): {result.stdout[:1000]}')
            else:
                Actor.log.warning('No stdout from Maigret')
            
            Actor.log.info(f'Search completed for {username}')
            
        except subprocess.TimeoutExpired:
            Actor.log.error('Maigret execution timed out')
        except Exception as e:
            Actor.log.error(f'Error running Maigret: {str(e)}')
            raise

if __name__ == '__main__':
    asyncio.run(main())
