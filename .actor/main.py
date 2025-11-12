from apify import Actor
import asyncio
import subprocess
import json
import os

async def main():
    async with Actor:
        # Récupérer l'input
        actor_input = await Actor.get_input() or {}
        usernames = actor_input.get('usernames', [])
        timeout = actor_input.get('timeout', 30)
        tags = actor_input.get('tags', '')
        all_sites = actor_input.get('allSites', False)
        
        # Vérification
        if not usernames or len(usernames) == 0:
            Actor.log.error('No usernames provided in input')
            Actor.log.info(f'Received input: {actor_input}')
            raise ValueError('At least one username is required in the "usernames" array')
        
        Actor.log.info(f'Starting Maigret search for {len(usernames)} username(s): {usernames}')
        
        for username in usernames:
            Actor.log.info(f'Searching for username: {username}')
            
            # Créer le dossier de sortie
            output_dir = '/tmp/maigret_results'
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                # Construire la commande Maigret
                cmd = [
                    'maigret', 
                    username, 
                    '--timeout', str(timeout),
                    '--json', 'simple',
                    '--folderoutput', output_dir,
                    '--no-color'
                ]
                
                if tags and tags.strip():
                    cmd.extend(['--tags', tags])
                    
                if all_sites:
                    cmd.append('-a')
                
                Actor.log.info(f'Running command: {" ".join(cmd)}')
                
                # Exécuter Maigret
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600
                )
                
                Actor.log.info(f'Maigret completed with return code: {result.returncode}')
                
                # Chercher le fichier JSON généré par Maigret
                json_file = os.path.join(output_dir, 'json', f'{username}.json')
                
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
                    
                    # Afficher les fichiers créés pour déboguer
                    Actor.log.info(f'Files in {output_dir}:')
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            Actor.log.info(f'  - {os.path.join(root, file)}')
                    
                    if result.stdout:
                        Actor.log.info(f'Maigret stdout (first 1000 chars): {result.stdout[:1000]}')
                    if result.stderr:
                        Actor.log.info(f'Maigret stderr (first 1000 chars): {result.stderr[:1000]}')
                
            except subprocess.TimeoutExpired:
                Actor.log.error(f'Maigret timed out for {username}')
            except json.JSONDecodeError as e:
                Actor.log.error(f'Failed to parse JSON for {username}: {e}')
            except Exception as e:
                Actor.log.error(f'Error processing {username}: {str(e)}')
                import traceback
                Actor.log.error(traceback.format_exc())
        
        Actor.log.info('All searches completed')

if __name__ == '__main__':
    asyncio.run(main())
