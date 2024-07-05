from django.shortcuts import render
from .reply_factory import generate_bot_responses, record_current_answer, get_next_question, generate_final_response
from django.http import JsonResponse  

def chat(request):
    if not request.session.session_key:
        request.session.create()

    if request.method == 'POST':
        message = request.POST.get('message')  
        session = request.session

        # Example: Record current user's answer
        success, message = record_current_answer(message, session['current_question_id'], session)
        if not success:
            return JsonResponse({'error': message}, status=400)

        # Example: Generate bot responses
        bot_responses = generate_bot_responses(message, session)

        # Update session and render template with responses
        session.save()
        return render(request, 'chat.html', {'bot_responses': bot_responses})

    return render(request, 'chat.html')
