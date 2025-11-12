from apify import Actor
import asyncio
import subprocess
import json
import tempfile
import os

async def main():
    async with Actor:
        # Récupérer l'input
        actor_input = await Actor.get_input() or {}
        usernames = actor_input.get('usernames', [])
        timeout = actor_input.get('timeout', 30)
        tags = actor_input.get('tags', '')
        all_sites = actor_input.get('allSites', False)
        
        if not usernames:
            raise ValueError('At least one username is required')
        
        Actor.log.info(f'Starting Maigret search for {len(usernames)} username(s)')
        
        for username in usernames:
            Actor.log.info(f'Searching for username: {username}')
            
            # Créer un fichier temporaire pour les résultats
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            try:
                # Construire la commande Maigret
                cmd = [
                    'maigret', 
                    username, 
                    '--timeout', str(timeout),
                    '--json', 'simple',
                    '--folderoutput', os.path.dirname(temp_filename),
                    '--no-color'
                ]
                
                if tags:
                    cmd.extend(['--tags', tags])
                    
                if all_sites:
                    cmd.append('-a')
                
                Actor.log.info(f'Running: {" ".join(cmd)}')
                
                # Exécuter Maigret
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600,
                    cwd='/tmp'
                )
                
                # Le fichier JSON est créé par Maigret
                json_file = f'/tmp/results/json/{username}.json'
                
                if os.path.exists(json_file):
                    Actor.log.info(f'Reading results from {json_file}')
                    
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    results_count = 0
                    
                    # Parser les résultats
                    for site_name, site_data in data.items():
                        if isinstance(site_data, dict):
                            status_info = site_data.get('status', {})
                            
                            # Ne garder que les profils trouvés
                            if status_info.get('status') == 'Claimed':
                                await Actor.push_data({
                                    'username': username,
                                    'site_name': site_name,
                                    'url': site_data.get('url_user', ''),
                                    'status': status_info.get('status', 'Unknown'),
                                    'http_status': status_info.get('http_status'),
                                    'response_time': status_info.get('query_time')
                                })
                                results_count += 1
                    
                    Actor.log.info(f'Found {results_count} profiles for {username}')
                else:
                    Actor.log.warning(f'No results file found at {json_file}')
                    Actor.log.info(f'Stdout: {result.stdout[:500]}')
                    Actor.log.info(f'Stderr: {result.stderr[:500]}')
                
            except subprocess.TimeoutExpired:
                Actor.log.error(f'Maigret timed out for {username}')
            except Exception as e:
                Actor.log.error(f'Error processing {username}: {str(e)}')
            finally:
                # Nettoyer les fichiers temporaires
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
        
        Actor.log.info('All searches completed')

if __name__ == '__main__':
    asyncio.run(main())
