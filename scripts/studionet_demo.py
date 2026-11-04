"""Opt-in live Studionet demo. Uses synthetic data and newly generated disposable wallets.
Requires Studionet simulator faucet support. Never imports existing wallet credentials.
Resumes recorded transaction hashes rather than resubmitting after poll timeouts.
"""
import json,hashlib,time
from pathlib import Path
from genlayer_py import create_client,create_account,studionet
ROOT=Path(__file__).resolve().parents[1]
# Creates disposable test wallets; never use this file for valuable assets.
import os
wallet_path=ROOT/'.demo-accounts.json'
if not wallet_path.exists():
 accounts=[create_account() for _ in range(3)]
 fd=os.open(wallet_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump([a.key.hex() for a in accounts],f)
accounts=[create_account(x) for x in json.loads(wallet_path.read_text())]
client=create_client(chain=studionet,account=accounts[0])
manifest_path=ROOT/'docs/deployment.json'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
# Published manifests belong to the published demonstration wallets. Start a new
# checkout/output directory to create a new demo; never overwrite someone else's run.
if manifest_path.exists():
 manifest=json.loads(manifest_path.read_text())
 if manifest['demo_wallets'] != [a.address for a in accounts]:
  raise RuntimeError('Existing deployment uses other wallets. Use a fresh copy with docs/deployment.json removed to start your own demo.')
else:
 for a in accounts:client.fund_account(a.address,10**19)
 terms={'shipment_id':'HIQ-DEMO-20261104','quantity':100,'unit':'sealed cartons',
 'route':[a.address.lower() for a in accounts],
 'requirements':'All 100 sealed cartons must arrive intact, dry and with matching seal S-0042.'}
 (ROOT/'fixtures/live-terms.json').write_text(json.dumps(terms,indent=2)+'\n')
 # Persist the hash immediately after broadcast; polling a pending transaction does
 # not submit a second deployment. A process crash during broadcast itself still
 # requires checking chain nonce/transaction history before any resubmission.
 tx=client.deploy_contract(code=(ROOT/'contracts/handover_iq.py').read_text(),args=[canon(terms)],leader_only=False)
 manifest={'network':'Studionet','chain_id':61999,'rpc':'https://studio.genlayer.com/api',
 'contract_address':None,'demo_wallets':[a.address for a in accounts],
 'source_sha256':sha((ROOT/'contracts/handover_iq.py').read_text()),'synthetic':True,
 'leader_only':False,'transactions':[{'step':'deploy','hash':tx}]}
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
# Resolve the already submitted deployment, including interrupted previous runs.
if not manifest['contract_address']:
 for _ in range(30):
  raw=client.provider.make_request('eth_getTransactionByHash',[manifest['transactions'][0]['hash']]).get('result')
  if raw and raw.get('to_address'):
   manifest['contract_address']=raw['to_address']
   manifest['contract_url']='https://explorer-studio.genlayer.com/contracts/'+raw['to_address']
   manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
   break
  time.sleep(2)
 else:raise TimeoutError('Deployment address not yet available; resume the same run.')
address=manifest['contract_address']
def save():manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
def wait(entry):
 for i in range(90):
  response=client.provider.make_request('eth_getTransactionByHash',[entry['hash']])
  raw=response.get('result')
  if raw and raw['status'] in ('FINALIZED','UNDETERMINED','CANCELED'):
   leaders=raw.get('consensus_data',{}).get('leader_receipt',[])
   entry.update(status=raw['status'],result_name=raw.get('result_name'),votes=raw.get('consensus_data',{}).get('votes'),
     execution=[{k:l.get(k) for k in ('execution_result','genvm_result')} for l in leaders])
   save()
   print(entry['step'],entry['hash'],entry['status'],entry['execution'],flush=True)
   if raw['status']!='FINALIZED' or not leaders or any(l.get('execution_result')!='SUCCESS' for l in leaders):
    raise RuntimeError('Transaction did not succeed; inspect manifest')
   return
  if i%10==0: print('waiting',entry['step'],raw.get('status') if raw else None,flush=True)
  time.sleep(3)
 raise TimeoutError(entry['hash'])
def step(name,index,method,args):
 matches=[x for x in manifest['transactions'] if x['step']==name]
 if matches:
  entry=matches[0]
  if entry.get('status')=='FINALIZED' and all(x['execution_result']=='SUCCESS' for x in entry.get('execution',[])):return
 else:
  tx=client.write_contract(address=address,function_name=method,args=args,account=accounts[index],leader_only=False)
  entry={'step':name,'hash':tx};manifest['transactions'].append(entry);save();print('submitted',name,tx,flush=True)
 wait(entry)
wait(manifest['transactions'][0])
terms=json.loads((ROOT/'fixtures/live-terms.json').read_text())
th=sha(canon(terms))
step('warehouse_accepts',1,'accept_terms',[th])
step('customer_accepts',2,'accept_terms',[th])
for leg in range(2):
 doc={'shipment_id':terms['shipment_id'],'leg':leg,'kind':'HANDOVER','quantity':100,'timestamp':1793746800+leg*3600,
      'narrative':f"Shipment HIQ-DEMO-20261104: on route leg {leg}, 100 sealed cartons were transferred and received intact and dry. Seal S-0042 matched; no damage, shortage or reservations. Handover timestamp: {1793746800+leg*3600} Unix seconds."}
 docid=sha(canon({'version':'handoveriq/1','terms_hash':th,'document':doc}))
 step('submit_leg_'+str(leg),leg,'submit_evidence',[canon(doc)])
 step('countersign_leg_'+str(leg),leg+1,'attest_evidence',[docid])
for i in range(3):step('close_'+str(i),i,'close_submission',[])
step('evaluate',0,'evaluate',[])
state=client.read_contract(address=address,function_name='get_state',args=[])
receipt=client.read_contract(address=address,function_name='get_receipt',args=[0])
(ROOT/'docs/live-state.json').write_text(json.dumps(json.loads(state),indent=2)+'\n')
(ROOT/'docs/live-receipts.json').write_text(json.dumps([json.loads(receipt)],indent=2)+'\n')
manifest['outcome']=json.loads(receipt)['decision']['outcome'];save()
print('OUTCOME',manifest['outcome'],flush=True)
