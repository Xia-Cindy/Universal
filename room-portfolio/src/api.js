const apiRequest = async (path, init = {}) => {
    const headers = new Headers(init.headers || {});
    const token = window.localStorage.getItem('universe_auth_token');
    if (token) headers.set('Authorization', `Bearer ${token}`);
    if (init.body && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(path, { ...init, headers });
    if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
            const payload = await response.json();
            detail = payload.detail || detail;
        } catch {
            // Preserve the status fallback when the API does not return JSON.
        }
        throw new Error(detail);
    }
    return response.status === 204 ? null : response.json();
};

export const roomApi = {
    studyWorkspace: () => apiRequest('/api/study/workspace'),
    switchGoal: (goalId) =>
        apiRequest(`/api/study/goals/${goalId}/switch`, { method: 'POST' }),
    completeTask: (taskId) =>
        apiRequest(`/api/study/tasks/${taskId}/complete`, { method: 'POST' }),
    startSession: (task) =>
        apiRequest('/api/study/execution/sessions', {
            method: 'POST',
            body: JSON.stringify({
                taskId: task.id,
                subject: task.subject,
                topic: task.topic,
                startTime: new Date().toISOString()
            })
        }),
    finishSession: (sessionId, notes = '') =>
        apiRequest(`/api/study/execution/sessions/${sessionId}/finish`, {
            method: 'POST',
            body: JSON.stringify({
                endTime: new Date(Date.now() + 60000).toISOString(),
                notes,
                feeling: 'focused'
            })
        }),
    tutorAsk: (question) =>
        apiRequest('/api/study/tutor/ask', {
            method: 'POST',
            body: JSON.stringify({ question, scope: 'current_goal' })
        }),
    reviewQueue: () => apiRequest('/api/study/review/queue?includeFuture=true'),
    completeReview: (reviewId) =>
        apiRequest(`/api/study/review/items/${reviewId}/complete`, {
            method: 'POST',
            body: JSON.stringify({ result: 'remembered' })
        }),
    analytics: () => apiRequest('/api/study/analytics'),
    feedbackRecommendations: () => apiRequest('/api/study/feedback/recommendations'),
    knowledgeDocuments: () => apiRequest('/api/study/knowledge/documents'),
    knowledgeDocument: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}`),
    refreshKnowledgeDocument: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/status`),
    verifyKnowledgeProviderRuntime: () =>
        apiRequest('/api/knowledge/provider/runtime-verification', { method: 'POST' }),
    createKnowledgeDocument: (payload) =>
        apiRequest('/api/study/knowledge/documents', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    processKnowledgeDocument: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/process`, { method: 'POST' }),
    deleteKnowledgeDocument: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}`, { method: 'DELETE' }),
    updateKnowledgeDocument: (documentId, payload) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        }),
    knowledgeAnnotations: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/annotations`),
    createKnowledgeAnnotation: (documentId, payload) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/annotations`, {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    markKnowledgeAnnotationMastered: (documentId, annotationId, mastered = true) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/annotations/${annotationId}/mastered`, {
            method: 'POST',
            body: JSON.stringify({ mastered })
        }),
    knowledgeShareGrants: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/share-grants`),
    knowledgeGoalLinks: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/goal-links`),
    updateKnowledgeGoalLinks: (documentId, payload) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/goal-links`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        }),
    knowledgeReadingProgress: (documentId) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/reading-progress`),
    saveKnowledgeReadingProgress: (documentId, payload) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/reading-progress`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        }),
    createKnowledgeShareGrant: (documentId, payload) =>
        apiRequest(`/api/study/knowledge/documents/${documentId}/share-grants`, {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    revokeKnowledgeShareGrant: (grantId) =>
        apiRequest(`/api/study/knowledge/share-grants/${grantId}`, { method: 'DELETE' }),
    wordbook: () => apiRequest('/api/study/wordbook/entries'),
    createWordbookEntry: (payload) =>
        apiRequest('/api/study/wordbook/entries', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    updateWordbookEntry: (entryId, payload) =>
        apiRequest(`/api/study/wordbook/entries/${entryId}`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        }),
    deleteWordbookEntry: (entryId) =>
        apiRequest(`/api/study/wordbook/entries/${entryId}`, { method: 'DELETE' }),
    refreshWordbookDictionary: (entryId) =>
        apiRequest(`/api/study/wordbook/entries/${entryId}/dictionary/refresh`, {
            method: 'POST'
        }),
    reviewWordbookEntry: (entryId, remembered) =>
        apiRequest(`/api/study/wordbook/entries/${entryId}/review`, {
            method: 'POST',
            body: JSON.stringify({ remembered })
        }),
    recallSchedules: (goalId = '') =>
        apiRequest(`/api/study/recall/schedules${goalId ? `?goalId=${encodeURIComponent(goalId)}` : ''}`),
    adjustRecallSchedule: (sourceType, sourceId, payload) =>
        apiRequest(`/api/study/recall/schedules/${encodeURIComponent(sourceType)}/${encodeURIComponent(sourceId)}`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        }),
    importWordbook: (payload) =>
        apiRequest('/api/study/wordbook/import', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    workHome: () => apiRequest('/api/work/home'),
    workCases: () => apiRequest('/api/work/cases'),
    createWorkCase: (payload) =>
        apiRequest('/api/work/cases', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    workCase: (caseId) => apiRequest(`/api/work/cases/${caseId}`),
    updateWorkCase: (caseId, payload) =>
        apiRequest(`/api/work/cases/${caseId}`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        }),
    workTechStacks: () => apiRequest('/api/work/tech-stacks'),
    createWorkTechStack: (payload) =>
        apiRequest('/api/work/tech-stacks', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    workTechStack: (techStackId) => apiRequest(`/api/work/tech-stacks/${techStackId}`),
    createWorkArticle: (techStackId, payload) =>
        apiRequest(`/api/work/tech-stacks/${techStackId}/articles`, {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    createWorkLearningRecord: (techStackId, payload) =>
        apiRequest(`/api/work/tech-stacks/${techStackId}/learning-records`, {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    workKnowledgeDocuments: (techStackId = '') =>
        apiRequest(`/api/work/knowledge/documents${techStackId ? `?techStackId=${encodeURIComponent(techStackId)}` : ''}`),
    workKnowledgeDocument: (documentId) =>
        apiRequest(`/api/work/knowledge/documents/${documentId}`),
    refreshWorkKnowledgeDocument: (documentId) =>
        apiRequest(`/api/work/knowledge/documents/${documentId}/status`),
    createWorkKnowledgeDocument: (payload) =>
        apiRequest('/api/work/knowledge/documents', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    processWorkKnowledgeDocument: (documentId) =>
        apiRequest(`/api/work/knowledge/documents/${documentId}/process`, { method: 'POST' }),
    novelDrafts: () => apiRequest('/api/novel/drafts'),
    createNovelDraft: (draft) =>
        apiRequest('/api/novel/drafts', {
            method: 'POST',
            body: JSON.stringify(draft)
        }),
    updateNovelDraft: (draftId, draft) =>
        apiRequest(`/api/novel/drafts/${draftId}`, {
            method: 'PATCH',
            body: JSON.stringify(draft)
        })
};
