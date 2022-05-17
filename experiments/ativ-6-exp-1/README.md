# Execução do Treinamento de Forma Distribuída na Nuvem

## Configuração das Instâncias na AWS

O provedor de serviços de nuvem utilizado para esse experimento foi a AWS, porém é possível utilizar outros (GCP, Azure, nuvens privadas etc.), basta
configurar as VMs de forma parecida assim como as regras de firewall, de modo que permita o tráfego de mensagens entre as duas VMs.

### Criação de Imagem Base

A fim de facilitar a criação de novos nós, é interessante criar uma imagem base contendo todas as dependências para execução do experimento. Para
isso siga o tutorial do estudo de caso 2 do Capítulo 3 [deste livro](http://wscad.sbc.org.br/2018/anais/wscad-2018-minicursos.pdf), mas antes de criar a imagem, execute as seguintes instruções:

- sudo apt install pip3 docker.io
- pip install fabric==2.7.0
- git clone https://github.com/eborin/Distributed-DCGAN.git
- cd Distributed-DCGAN
- git switch ativ-6-exp-1
- cd experiments/ativ-6-exp-1
- ./build.sh

Desse modo as VMs possuirão todas as dependências, dados e imagens necessários para a execução do terinamento.

### Criação de VMs e Configuração de Rede

Crie 2 VMs utilizando a imagem criada e configure os grupos de segurança de maneira a permitir o tráfego entre as instâncias e também o acesso externo por SSH, assim como especificado no tutorial referenciado acima.

## Execução da Aplicação

De modo a remover a necessidade de iniciar contêineres individualmente em cada máquina, utilizou-se o `fabric` para executar comandos por SSH nos hosts registrados. Com isso, acessando uma das instâncias criadas por SSH e ido para o diretório `~/Distributed-DCGAN/experiments/ativ-6-exp-1` a execução do experimento se dará com o seguinte comando:

```
python3 experiment.py --hosts <IP1>,<IP2>
```

Sendo \<IP1\> e \<IP2\> os IPs privados das instâncias criadas.
\<IP1\> é utilizado como o endereço do nó mestre por padrão, assim normalmente é o IP da máquina que está sendo utilizada para executar o script.

O `nohup` pode ser utilizado para executar o experimento desassociado na sessão atual como daemon

```
nohup python3 experiment.py --hosts <IP1>,<IP2> > output &
```

O script de execução acessa cada máquina individualmente e configura o arquivo `.env` com algumas variáveis de ambiente, dentre elas o `NODE_RANK` que é único para cada nó. Após isso, executa o treinamento em apenas
um nó com um processo e batch_size=16, para obter uma baseline, e então com 2 nós e 1, 2 e 4 processos por nó. Para cada uma dessas configurações um arquivo CSV é gerado, onde cada linha corresponde a uma amostra, sendo o valor na primeira coluna o tempo total da execução medido no script e os valores seguintes correspondem ao tempo que cada processo demorou para finalizar a Epoch 0 do treinamento.
