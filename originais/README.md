# As fotos como vieram

Originais em resolução cheia, guardadas aqui para quando for preciso recortar
outro enquadramento ou gerar um tamanho novo. **Não são publicadas**: o
`deploy.sh` só envia `mishpat/index.html` e `mishpat/assets/`, e é de lá que a
página lê. O que está em `mishpat/assets/` saiu destas, reduzido e recomprimido
com `sips` — 604 KB somados, contra 6,4 MB aqui.

Autoria: Pavel Danilyuk, no Pexels (licença Pexels — uso livre, sem atribuição
obrigatória).

| Original | Vira | Onde aparece |
|---|---|---|
| `pexels-pavel-danilyuk-8112110.jpg` (6016×4016) | `heroi-escritorio.jpg` (2000px) | fundo do herói, sob o degradê navy |
| `pexels-pavel-danilyuk-8111815.jpg` (4016×6016) | `vocabulario-justica.jpg` (1200px) | "Menos conferência, mais advocacia" |
| `pexels-pavel-danilyuk-8111865.jpg` (5805×3875) | `processo-assinatura.jpg` (1400px) | "Do cadastro ao primeiro aviso" |
| `pexels-pavel-danilyuk-8112197.jpg` (4016×6016) | `faq-atendimento.jpg` (1100px) | coluna lateral das perguntas |

Para refazer uma delas:

```bash
sips -Z 2000 -s formatOptions 68 originais/<arquivo>.jpg --out mishpat/assets/<destino>.jpg
```

O `-Z` respeita a proporção e a moldura no CSS tem altura fixa com
`object-fit: cover` — o recorte é do quadro, não do arquivo.
