#!/bin/bash

echo "🧪 TESTE DE SALVAMENTO DE VAGAS"
echo "==============================="

echo ""
echo "📋 INSTRUÇÕES PARA TESTE MANUAL:"
echo "================================"

echo "1️⃣ ACESSE O SITE:"
echo "   https://rh.institutoacqua.org.br"

echo ""
echo "2️⃣ FAÇA LOGIN:"
echo "   - Use suas credenciais de recrutador"
echo "   - Verifique se o login funciona corretamente"

echo ""
echo "3️⃣ TESTE CRIAÇÃO DE VAGA:"
echo "   - Vá para 'Gestão de Vagas'"
echo "   - Clique em 'Nova Vaga'"
echo "   - Preencha os campos obrigatórios:"
echo "     • Título da vaga"
echo "     • Descrição"
echo "     • Requisitos"
echo "     • Hospital/Unidade"
echo "     • Departamento/Setor"
echo "     • Localização"
echo "   - Clique em 'Salvar'"

echo ""
echo "4️⃣ TESTE EDIÇÃO DE VAGA:"
echo "   - Selecione uma vaga existente"
echo "   - Clique em 'Editar'"
echo "   - Modifique algum campo"
echo "   - Clique em 'Salvar'"

echo ""
echo "5️⃣ VERIFICAÇÕES IMPORTANTES:"
echo "   ✅ Não deve aparecer erro 403 Forbidden"
echo "   ✅ Não deve aparecer erro de CSRF"
echo "   ✅ A vaga deve ser salva com sucesso"
echo "   ✅ Deve aparecer mensagem de sucesso"

echo ""
echo "🔍 SE HOUVER PROBLEMAS:"
echo "======================="

echo "❌ Erro 403 Forbidden:"
echo "   - As configurações de CSRF ainda não foram aplicadas"
echo "   - Execute: sudo ./reiniciar_containers.sh"

echo ""
echo "❌ Erro de CSRF Token:"
echo "   - Verifique se o token está sendo enviado"
echo "   - Verifique se o formulário tem {% csrf_token %}"

echo ""
echo "❌ Erro de permissão:"
echo "   - Verifique se o usuário tem role de recrutador"
echo "   - Verifique se está logado corretamente"

echo ""
echo "📊 STATUS DAS CORREÇÕES:"
echo "======================="

# Verificar se as correções foram aplicadas
if grep -q "CSRF_COOKIE_SECURE=True" .env; then
    echo "✅ CSRF_COOKIE_SECURE configurado corretamente"
else
    echo "❌ CSRF_COOKIE_SECURE não configurado"
fi

if grep -q "SESSION_COOKIE_SECURE=True" .env; then
    echo "✅ SESSION_COOKIE_SECURE configurado corretamente"
else
    echo "❌ SESSION_COOKIE_SECURE não configurado"
fi

if grep -q "https://rh.institutoacqua.org.br" .env; then
    echo "✅ HTTPS incluído nos CSRF_TRUSTED_ORIGINS"
else
    echo "❌ HTTPS não incluído nos CSRF_TRUSTED_ORIGINS"
fi

echo ""
echo "🎯 RESULTADO ESPERADO:"
echo "====================="
echo "O salvamento de vagas deve funcionar normalmente"
echo "sem erros de CSRF ou permissão."

echo ""
echo "📞 SUPORTE:"
echo "==========="
echo "Se o problema persistir após as correções,"
echo "verifique os logs do container Django para"
echo "mais detalhes sobre o erro específico."
