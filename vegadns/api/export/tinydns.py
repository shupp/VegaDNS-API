

class ExportTinydnsData(object):
    def data_line_from_model(self, model):

        if model.type == "A":
            return "+" + model.host + ":" + model.val + \
                ":" + str(model.ttl) + "\n"
        elif model.type == "M":
            return "@" + model.host + "::" + model.val + ":" + \
                   str(model.distance) + ":" + str(model.ttl) + "\n"
        elif model.type == "P":
            return "^" + model.host + ":" + model.val + \
                ":" + str(model.ttl) + "\n"
        elif model.type == "T":
            return "'" + model.host + ":" + model.val.replace(":", r"\072") + \
                   ":" + str(model.ttl) + "\n"
        elif model.type == "F":
            return "\n"
        elif model.type == "C":
            return "\n"
        elif model.type == "S":
            return "\n"
        elif model.type == "V":
            return "\n"
        # together?
        elif model.type == "3":
            return "\n"
        elif model.type == "6":
            return "\n"

    def export_domain(self, domain_name, records):
        output = "# " + domain_name + "\n"
        formatted_records = ""
        for record in records:
            formatted_record = self.data_line_from_model(record)
            if formatted_record is None:
                # fixme, need to finish record support
                pass
            else:
                formatted_records = formatted_records + formatted_record

        return output + formatted_records

    def export_domains(self, domains):
        output = ""
        for domain in domains:
            formatted = self.export_domain(
                domain['domain_name'],
                domain['records']
            )
            output = output + formatted + "\n"

        return output
