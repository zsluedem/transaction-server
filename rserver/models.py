from typing import List
import base64
from pydantic import BaseModel
from rchain.report import DeployWithTransaction

class DeployInfo(BaseModel):
    deployer: str
    term: str
    timestamp: int
    sig: str
    sigAlgorithm: str
    phloPrice: int
    phloLimit: int
    validAfterBlockNumber: int
    cost: int
    errored: bool
    systemDeployError: int

class TransactionInfo(BaseModel):
    deploy: DeployInfo
    fromAddr: str
    toAddr: str
    amount: int
    retUnforeable: str
    success: bool
    reason: str



def deployWithTransactionToTransactionInfo(deploy_transactions: List[DeployWithTransaction]) -> List[List[TransactionInfo]]:
    result = []
    for deploy in deploy_transactions:
        deploy_info = DeployInfo(**{
            'deployer': deploy.deploy_info.deployer,
            'term': deploy.deploy_info.term,
            'timestamp': deploy.deploy_info.timestamp,
            'sig': deploy.deploy_info.sig,
            'sigAlgorithm': deploy.deploy_info.sigAlgorithm,
            'phloPrice': deploy.deploy_info.phloPrice,
            'phloLimit': deploy.deploy_info.phloLimit,
            'validAfterBlockNumber': deploy.deploy_info.validAfterBlockNumber,
            'cost': deploy.deploy_info.cost,
            'errored': deploy.deploy_info.errored,
            'systemDeployError': deploy.deploy_info.systemDeployError
        })
        one_deploy = [TransactionInfo(**{
            'fromAddr': transaction.from_addr,
            'toAddr': transaction.to_addr,
            'amount': transaction.amount,
            'retUnforeable': base64.encodebytes(transaction.ret_unforgeable.SerializeToString()).decode('utf8'),
            'deploy': deploy_info,
            'success': transaction.success[0],
            'reason': transaction.success[1]
        }) for transaction in deploy.transactions]

        result.append(one_deploy)
    return result