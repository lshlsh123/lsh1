const API_BASE = "http://localhost:8000";

const fetchJSON = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `请求失败: ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return await response.json();
};

const showToast = (message, type = "info") => {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add("visible"), 20);
  setTimeout(() => {
    toast.classList.remove("visible");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
};

const renderModels = (models) => {
  const list = document.getElementById("models-list");
  list.innerHTML = "";
  const template = document.getElementById("model-card-template");

  models.forEach((model) => {
    const node = template.content.cloneNode(true);
    const card = node.querySelector(".card");
    card.querySelector("h3").textContent = `${model.name} (${model.status})`;
    card.querySelector(".meta").textContent = `ID: ${model.id} · 任务类型: ${model.task_type} · 版本: ${model.current_version}`;
    card.querySelector(".desc").textContent = model.description || "暂无描述";

    const tags = document.createElement("p");
    tags.className = "tags";
    tags.textContent = `标签: ${model.tags.join(", ")}`;
    card.insertBefore(tags, card.querySelector(".desc"));

    card.querySelector(".delete").addEventListener("click", async () => {
      await fetchJSON(`${API_BASE}/models/${model.id}`, { method: "DELETE" });
      showToast(`模型 ${model.name} 已删除`, "success");
      await loadModels();
    });

    list.appendChild(node);
  });
};

const renderTemplates = (templates) => {
  const list = document.getElementById("templates-list");
  list.innerHTML = "";
  const templateNode = document.getElementById("template-card-template");

  templates.forEach((template) => {
    const node = templateNode.content.cloneNode(true);
    const card = node.querySelector(".card");
    card.querySelector("h3").textContent = template.name;
    card.querySelector(".desc").textContent = template.description || "暂无描述";
    card.querySelector(".params").textContent = JSON.stringify(template.parameters, null, 2);
    card.querySelector(".delete").addEventListener("click", async () => {
      await fetchJSON(`${API_BASE}/templates/${template.id}`, { method: "DELETE" });
      showToast(`模板 ${template.name} 已删除`, "success");
      await loadTemplates();
    });
    list.appendChild(node);
  });
};

const renderJobs = (jobs) => {
  const list = document.getElementById("jobs-list");
  list.innerHTML = "";
  const templateNode = document.getElementById("job-card-template");

  jobs.forEach((job) => {
    const node = templateNode.content.cloneNode(true);
    const card = node.querySelector(".card");
    card.querySelector("h3").textContent = `任务 ${job.id}`;
    card.querySelector(".desc").textContent = `模型: ${job.model_id} · 数据集: ${job.dataset} · 状态: ${job.status}`;
    card.querySelector(".metrics").textContent = JSON.stringify(job.metrics, null, 2);
    card.querySelector(".delete").addEventListener("click", async () => {
      await fetchJSON(`${API_BASE}/jobs/${job.id}`, { method: "DELETE" });
      showToast(`训练任务 ${job.id} 已删除`, "success");
      await loadJobs();
    });
    list.appendChild(node);
  });
};

const loadModels = async () => {
  try {
    const models = await fetchJSON(`${API_BASE}/models`);
    renderModels(models);
  } catch (error) {
    showToast(error.message, "error");
  }
};

const loadTemplates = async () => {
  try {
    const templates = await fetchJSON(`${API_BASE}/templates`);
    renderTemplates(templates);
  } catch (error) {
    showToast(error.message, "error");
  }
};

const loadJobs = async () => {
  try {
    const jobs = await fetchJSON(`${API_BASE}/jobs`);
    renderJobs(jobs);
  } catch (error) {
    showToast(error.message, "error");
  }
};

// Event bindings

document.getElementById("refresh-models").addEventListener("click", loadModels);
document.getElementById("refresh-templates").addEventListener("click", loadTemplates);
document.getElementById("refresh-jobs").addEventListener("click", loadJobs);

document.getElementById("model-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    name: document.getElementById("model-name").value.trim(),
    task_type: document.getElementById("model-task").value.trim(),
    owner: document.getElementById("model-owner").value.trim(),
    current_version: document.getElementById("model-version").value.trim() || "v1.0.0",
    tags: document
      .getElementById("model-tags")
      .value.split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
    description: document.getElementById("model-desc").value.trim(),
  };

  try {
    await fetchJSON(`${API_BASE}/models`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("模型创建成功", "success");
    event.target.reset();
    await loadModels();
  } catch (error) {
    showToast(error.message, "error");
  }
});

document.getElementById("template-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  let parameters = [];
  const rawParams = document.getElementById("template-params").value.trim();
  if (rawParams) {
    try {
      parameters = JSON.parse(rawParams);
    } catch (error) {
      showToast("参数定义需为合法 JSON", "error");
      return;
    }
  }

  const payload = {
    name: document.getElementById("template-name").value.trim(),
    description: document.getElementById("template-desc").value.trim(),
    parameters,
  };

  try {
    await fetchJSON(`${API_BASE}/templates`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("模板创建成功", "success");
    event.target.reset();
    await loadTemplates();
  } catch (error) {
    showToast(error.message, "error");
  }
});

document.getElementById("job-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    model_id: document.getElementById("job-model").value.trim(),
    dataset: document.getElementById("job-dataset").value.trim(),
    pipeline: document.getElementById("job-pipeline").value.trim(),
  };

  try {
    await fetchJSON(`${API_BASE}/jobs`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("训练任务已提交", "success");
    event.target.reset();
    await loadJobs();
  } catch (error) {
    showToast(error.message, "error");
  }
});

// Initial data
loadModels();
loadTemplates();
loadJobs();
